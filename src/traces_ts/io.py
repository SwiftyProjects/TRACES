"""Data loading, validation and pair generation."""

from __future__ import annotations

import warnings
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from itertools import combinations
from pathlib import Path
from typing import Literal

import pandas as pd

MissingPolicy = Literal["raise", "drop", "interpolate"]
MISSING_OPTIONS: tuple[str, ...] = ("raise", "drop", "interpolate")
MIN_OBSERVATIONS = 3


@dataclass(frozen=True)
class TimeSeriesData:
    """A validated set of aligned, numeric time series.

    Attributes:
        frame: DataFrame indexed by time, one numeric column per series.
        time_column: Name of the column that was used as the time index.
        source: File the data was loaded from, if any.
    """

    frame: pd.DataFrame
    time_column: str
    source: Path | None = None

    @property
    def series(self) -> list[str]:
        return [str(c) for c in self.frame.columns]

    @property
    def n_observations(self) -> int:
        return len(self.frame)

    def __repr__(self) -> str:
        src = f", source={self.source.name!r}" if self.source else ""
        return (
            f"TimeSeriesData(n_series={len(self.series)}, "
            f"n_observations={self.n_observations}, time_column={self.time_column!r}{src})"
        )


def load_data(
    path: str | Path,
    *,
    time_column: str | int | None = None,
    sheet_name: str | int = 0,
    missing: MissingPolicy = "raise",
) -> TimeSeriesData:
    """Load time series from an Excel (.xlsx/.xls) or CSV file.

    Layout: one row per time point, a time column (the first column unless
    ``time_column`` is given) and one numeric column per series.

    Args:
        path: File to read.
        time_column: Name or position of the time column. Defaults to the first column.
        sheet_name: Worksheet to read for Excel files.
        missing: How to treat missing values: ``"raise"`` (default), ``"drop"`` rows,
            or ``"interpolate"`` interior gaps linearly (edge gaps are dropped).
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Data file not found: {path}")

    suffix = path.suffix.lower()
    if suffix in {".xlsx", ".xlsm", ".xls"}:
        raw = pd.read_excel(path, sheet_name=sheet_name, header=0)
    elif suffix in {".csv", ".txt"}:
        raw = pd.read_csv(path, header=0)
    else:
        raise ValueError(f"Unsupported file type {suffix!r}; use .xlsx, .xls or .csv")

    data = from_frame(raw, time_column=time_column, missing=missing)
    return TimeSeriesData(frame=data.frame, time_column=data.time_column, source=path)


def from_frame(
    df: pd.DataFrame,
    *,
    time_column: str | int | None = None,
    missing: MissingPolicy = "raise",
) -> TimeSeriesData:
    """Validate an in-memory DataFrame with the same layout as :func:`load_data`.

    If ``time_column`` is None and the frame already has a non-default index
    (e.g. a DatetimeIndex), that index is used as time.
    """
    if missing not in MISSING_OPTIONS:
        raise ValueError(f"missing must be one of {MISSING_OPTIONS}, got {missing!r}")
    if df.shape[1] == 0:
        raise ValueError("DataFrame has no columns")

    df = df.copy()
    if time_column is None and not isinstance(df.index, pd.RangeIndex):
        time_name = str(df.index.name or "time")
        frame = df
    else:
        if time_column is None:
            time_name = df.columns[0]
        elif isinstance(time_column, int):
            time_name = df.columns[time_column]
        else:
            if time_column not in df.columns:
                raise ValueError(f"Time column {time_column!r} not found in {list(df.columns)}")
            time_name = time_column
        frame = df.set_index(time_name)
        time_name = str(time_name)

    frame.index = _parse_time_index(frame.index)
    frame.columns = [str(c) for c in frame.columns]

    if frame.shape[1] < 2:
        raise ValueError("At least two series (besides the time column) are required")
    if frame.columns.duplicated().any():
        dupes = sorted(set(frame.columns[frame.columns.duplicated()]))
        raise ValueError(f"Duplicate series names: {dupes}")

    non_numeric = [c for c in frame.columns if not pd.api.types.is_numeric_dtype(frame[c])]
    if non_numeric:
        raise ValueError(
            f"All series must be numeric; non-numeric columns: {non_numeric}. "
            "If one of these is your time column, pass time_column=..."
        )
    frame = frame.astype("float64")

    if frame.index.has_duplicates:
        raise ValueError("Time column contains duplicate values")
    if not frame.index.is_monotonic_increasing:
        warnings.warn("Time column was not in ascending order; rows were sorted", stacklevel=2)
        frame = frame.sort_index()

    frame = _handle_missing(frame, missing)

    if len(frame) < MIN_OBSERVATIONS:
        raise ValueError(f"At least {MIN_OBSERVATIONS} observations are required, got {len(frame)}")

    return TimeSeriesData(frame=frame, time_column=time_name)


def _parse_time_index(index: pd.Index) -> pd.Index:
    if pd.api.types.is_numeric_dtype(index) or isinstance(index, pd.DatetimeIndex):
        return index
    try:
        return pd.DatetimeIndex(pd.to_datetime(index, format="mixed"))
    except (ValueError, TypeError):
        return index


def _handle_missing(frame: pd.DataFrame, missing: MissingPolicy) -> pd.DataFrame:
    n_missing = int(frame.isna().sum().sum())
    if n_missing == 0:
        return frame
    if missing == "raise":
        cols = frame.columns[frame.isna().any()].tolist()
        raise ValueError(
            f"Data contains {n_missing} missing values (columns: {cols}). "
            "Clean the data or use missing='drop' / missing='interpolate'."
        )
    if missing == "drop":
        cleaned = frame.dropna()
        warnings.warn(
            f"Dropped {len(frame) - len(cleaned)} rows containing missing values", stacklevel=3
        )
        return cleaned
    cleaned = frame.interpolate(method="linear", limit_area="inside").dropna()
    warnings.warn(
        f"Interpolated missing values ({n_missing} cells); "
        f"dropped {len(frame) - len(cleaned)} rows with edge gaps",
        stacklevel=3,
    )
    return cleaned


ExcludeSpec = Mapping[str, Iterable[str]] | Iterable[tuple[str, str]] | None


def generate_pairs(series: Iterable[str], exclude: ExcludeSpec = None) -> list[tuple[str, str]]:
    """Return all unordered series pairs, minus excluded ones.

    Args:
        series: Series names, in the order pairs should be generated.
        exclude: Either a parent -> children mapping (each parent/child pair is
            excluded, e.g. a total and its components) or an iterable of
            ``(a, b)`` pairs. Order within a pair does not matter.
    """
    names = list(series)
    excluded: set[frozenset[str]] = set()
    if isinstance(exclude, Mapping):
        for parent, children in exclude.items():
            excluded.update(frozenset((parent, child)) for child in children)
    elif exclude is not None:
        excluded.update(frozenset(pair) for pair in exclude)

    unknown = {name for pair in excluded for name in pair} - set(names)
    if unknown:
        warnings.warn(f"Exclusions reference unknown series: {sorted(unknown)}", stacklevel=2)

    return [(a, b) for a, b in combinations(names, 2) if frozenset((a, b)) not in excluded]

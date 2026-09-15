"""Series pre-processing applied before correlation analysis."""

from __future__ import annotations

import pandas as pd
from scipy import signal

from .config import DETREND_OPTIONS, Detrend


def detrend_frame(frame: pd.DataFrame, method: Detrend = "none") -> pd.DataFrame:
    """Apply the same detrending to every column.

    Args:
        frame: Time-indexed numeric DataFrame.
        method: ``"none"`` (levels), ``"linear"`` (remove a least-squares line) or
            ``"difference"`` (first differences; drops the first observation).
    """
    if method == "none":
        return frame
    if method == "linear":
        return pd.DataFrame(
            signal.detrend(frame.to_numpy(), axis=0, type="linear"),
            index=frame.index,
            columns=frame.columns,
        )
    if method == "difference":
        return frame.diff().iloc[1:]
    raise ValueError(f"detrend must be one of {DETREND_OPTIONS}, got {method!r}")


def zscore(series: pd.Series) -> pd.Series:
    """Standardize to zero mean and unit variance (ddof=1)."""
    std = series.std()
    if std == 0 or pd.isna(std):
        raise ValueError(f"Cannot standardize series {series.name!r} with zero variance")
    return (series - series.mean()) / std

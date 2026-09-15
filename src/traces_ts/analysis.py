"""End-to-end TRACES analysis pipeline."""

from __future__ import annotations

import warnings
from collections.abc import Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from .classify import classify_relationship
from .config import AnalysisConfig
from .correlation import METHODS, basic_correlations, rolling_correlation, strongest_method
from .io import ExcludeSpec, TimeSeriesData, from_frame, generate_pairs
from .lags import CCFResult, cross_correlation, prewhitened_cross_correlation
from .preprocess import detrend_frame
from .stats import effective_sample_size, fdr_adjust

RESULT_COLUMNS: tuple[str, ...] = (
    "series_1",
    "series_2",
    "relationship_type",
    "evidence_score",
    "recommended_methods",
    "strongest_method",
    "max_abs_correlation",
    "pearson",
    "pearson_p",
    "pearson_p_raw",
    "spearman",
    "spearman_p",
    "spearman_p_raw",
    "kendall",
    "kendall_p",
    "kendall_p_raw",
    "significant_methods",
    "n_obs",
    "n_effective",
    "rolling_mean",
    "rolling_std",
    "ccf_zero_lag",
    "ccf_peak",
    "ccf_peak_lag",
    "ccf_band",
    "ccf_peak_significant",
    "lag_ratio",
    "lag_detected",
)


@dataclass(frozen=True)
class PairDetail:
    """Per-pair arrays kept for plotting and drill-down."""

    rolling: pd.Series
    ccf: CCFResult
    """CCF used for lag detection (pre-whitened when enabled)."""
    ccf_raw: CCFResult
    """CCF of the (detrended) series without pre-whitening."""


@dataclass
class AnalysisResult:
    """Outcome of :func:`analyze`.

    Attributes:
        table: One row per analysed pair (see ``RESULT_COLUMNS``), sorted by
            ``max_abs_correlation`` descending.
        config: Configuration used.
        data: The (detrended) series that were analysed.
        details: Per-pair rolling correlations and CCFs, keyed by ``(series_1, series_2)``.
        skipped: Pairs that could not be analysed, with the reason.
    """

    table: pd.DataFrame
    config: AnalysisConfig
    data: TimeSeriesData
    details: dict[tuple[str, str], PairDetail] = field(default_factory=dict, repr=False)
    skipped: list[tuple[str, str, str]] = field(default_factory=list)

    def __repr__(self) -> str:
        counts = self.table["relationship_type"].value_counts().to_dict()
        return f"AnalysisResult(n_pairs={len(self.table)}, relationship_types={counts})"

    def pair(self, series_1: str, series_2: str) -> PairDetail:
        """Details for a pair, in either order."""
        if (series_1, series_2) in self.details:
            return self.details[(series_1, series_2)]
        if (series_2, series_1) in self.details:
            return self.details[(series_2, series_1)]
        raise KeyError(f"No details for pair ({series_1!r}, {series_2!r})")

    def top(self, n: int = 10, by: str = "evidence_score") -> pd.DataFrame:
        return self.table.sort_values(by, ascending=False).head(n)

    def by_type(self, relationship_type: str) -> pd.DataFrame:
        return self.table[self.table["relationship_type"] == relationship_type]

    def summary(self) -> dict[str, Any]:
        from .report import summary_statistics

        return summary_statistics(self)

    def to_csv(self, path: str | Path) -> Path:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        self.table.to_csv(path, index=False)
        return path

    def to_excel(self, path: str | Path) -> Path:
        """Write results, summary and configuration to separate worksheets."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        summary = self.summary()
        flat_summary = pd.DataFrame(
            [(k, str(v)) for k, v in summary.items()], columns=["metric", "value"]
        )
        cfg = pd.DataFrame(list(self.config.to_dict().items()), columns=["parameter", "value"])
        cfg["value"] = cfg["value"].astype(str)
        with pd.ExcelWriter(path) as writer:
            self.table.to_excel(writer, sheet_name="results", index=False)
            flat_summary.to_excel(writer, sheet_name="summary", index=False)
            cfg.to_excel(writer, sheet_name="config", index=False)
        return path


def analyze(
    data: TimeSeriesData | pd.DataFrame,
    config: AnalysisConfig | None = None,
    *,
    pairs: Sequence[tuple[str, str]] | None = None,
    exclude: ExcludeSpec = None,
    keep_details: bool = True,
) -> AnalysisResult:
    """Run the full TRACES analysis on every series pair.

    Args:
        data: Output of :func:`traces_ts.load_data`, or a DataFrame in the same layout.
        config: Analysis parameters (defaults to ``AnalysisConfig()``).
        pairs: Explicit pairs to analyse. Defaults to all pairs.
        exclude: Parent -> children mapping or pairs to leave out (ignored if ``pairs`` is given).
        keep_details: Keep rolling series and CCF arrays for plotting.
    """
    config = config or AnalysisConfig()
    if isinstance(data, pd.DataFrame):
        data = from_frame(data)

    frame = detrend_frame(data.frame, config.detrend)
    n = len(frame)
    if config.rolling_window > n:
        raise ValueError(f"rolling_window ({config.rolling_window}) exceeds observations ({n})")
    if config.max_lag > n - 3:
        warnings.warn(
            f"max_lag ({config.max_lag}) exceeds n - 3 ({n - 3}); lags are clipped", stacklevel=2
        )
    analysed = TimeSeriesData(frame=frame, time_column=data.time_column, source=data.source)

    if pairs is None:
        pairs = generate_pairs(analysed.series, exclude)
    missing = {s for pair in pairs for s in pair} - set(analysed.series)
    if missing:
        raise ValueError(f"Pairs reference unknown series: {sorted(missing)}")

    constant = {c for c in frame.columns if frame[c].std() == 0}
    rows: list[dict[str, Any]] = []
    details: dict[tuple[str, str], PairDetail] = {}
    skipped: list[tuple[str, str, str]] = []

    for s1, s2 in pairs:
        if s1 in constant or s2 in constant:
            skipped.append((s1, s2, "constant series"))
            continue
        row, detail = _analyze_pair(frame[s1], frame[s2], config)
        rows.append({"series_1": s1, "series_2": s2, **row})
        if keep_details:
            details[(s1, s2)] = detail

    if skipped:
        warnings.warn(f"Skipped {len(skipped)} pairs involving constant series", stacklevel=2)

    table = pd.DataFrame(rows, columns=list(RESULT_COLUMNS))
    if table.empty:
        return AnalysisResult(table, config, analysed, details, skipped)

    if config.fdr_correction:
        for method in METHODS:
            table[f"{method}_p"] = fdr_adjust(table[f"{method}_p"].to_numpy())

    _classify_rows(table, config)
    table = table.sort_values("max_abs_correlation", ascending=False, ignore_index=True)
    return AnalysisResult(table, config, analysed, details, skipped)


def _analyze_pair(
    x: pd.Series, y: pd.Series, config: AnalysisConfig
) -> tuple[dict[str, Any], PairDetail]:
    n = len(x)
    n_eff = effective_sample_size(x, y) if config.autocorrelation_adjustment else float(n)
    corr = basic_correlations(x, y, n_eff if config.autocorrelation_adjustment else None)
    best, best_abs = strongest_method(corr)

    rolling = rolling_correlation(x, y, config.rolling_window)
    ccf_raw = cross_correlation(x, y, config.max_lag, config.alpha)
    ccf = (
        prewhitened_cross_correlation(x, y, config.max_lag, config.alpha, config.max_ar_order)
        if config.prewhiten
        else ccf_raw
    )

    row: dict[str, Any] = {
        "strongest_method": best,
        "max_abs_correlation": best_abs,
        "n_obs": n,
        "n_effective": round(n_eff, 1),
        "rolling_mean": rolling.mean(),
        "rolling_std": rolling.std(),
        "ccf_zero_lag": ccf.zero_lag,
        "ccf_peak": ccf.peak,
        "ccf_peak_lag": ccf.peak_lag,
        "ccf_band": ccf.band,
        "ccf_peak_significant": ccf.peak_significant,
        "lag_ratio": ccf.lag_ratio,
    }
    for method, res in corr.items():
        row[method] = res.coefficient
        row[f"{method}_p"] = res.p_adjusted
        row[f"{method}_p_raw"] = res.p_raw
    return row, PairDetail(rolling=rolling, ccf=ccf, ccf_raw=ccf_raw)


def _classify_rows(table: pd.DataFrame, config: AnalysisConfig) -> None:
    sig = np.column_stack([table[f"{m}_p"].to_numpy() < config.alpha for m in METHODS])
    table["significant_methods"] = sig.sum(axis=1)
    table["lag_detected"] = (
        table["ccf_peak_significant"]
        & (table["ccf_peak_lag"] != 0)
        & (table["lag_ratio"] >= config.lag_min_ratio)
    )

    types, recs, scores = [], [], []
    for row in table.itertuples(index=False):
        result = classify_relationship(
            pearson=row.pearson,
            spearman=row.spearman,
            kendall=row.kendall,
            significant_methods=int(row.significant_methods),
            rolling_std=row.rolling_std if pd.notna(row.rolling_std) else np.inf,
            lag_detected=bool(row.lag_detected),
            ccf_peak=row.ccf_peak,
            config=config,
        )
        types.append(result.relationship_type)
        recs.append(", ".join(result.recommended_methods))
        scores.append(result.evidence_score)
    table["relationship_type"] = types
    table["recommended_methods"] = recs
    table["evidence_score"] = scores

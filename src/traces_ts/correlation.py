"""Contemporaneous (zero-lag) correlation measures."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy import stats

from .stats import correlation_pvalue

METHODS: tuple[str, ...] = ("pearson", "spearman", "kendall")


@dataclass(frozen=True)
class CorrelationResult:
    """One correlation coefficient with raw and adjusted p-values."""

    method: str
    coefficient: float
    p_raw: float
    """p-value assuming independent observations (as reported by SciPy)."""
    p_adjusted: float
    """p-value using the effective sample size (equals p_raw when not adjusted)."""


def basic_correlations(
    x: pd.Series, y: pd.Series, n_effective: float | None = None
) -> dict[str, CorrelationResult]:
    """Pearson, Spearman and Kendall correlations with significance tests.

    Args:
        x, y: Aligned series of equal length.
        n_effective: Effective sample size for autocorrelation-adjusted p-values.
            If None, the adjusted p-value equals SciPy's raw p-value.
    """
    a = np.asarray(x, dtype=float)
    b = np.asarray(y, dtype=float)
    raw = {
        "pearson": stats.pearsonr(a, b),
        "spearman": stats.spearmanr(a, b),
        "kendall": stats.kendalltau(a, b),
    }
    results = {}
    for method, res in raw.items():
        coef, p_raw = float(res.statistic), float(res.pvalue)
        p_adj = p_raw if n_effective is None else correlation_pvalue(coef, n_effective, method)
        results[method] = CorrelationResult(method, coef, p_raw, p_adj)
    return results


def strongest_method(results: dict[str, CorrelationResult]) -> tuple[str, float]:
    """Method with the largest absolute coefficient, and that absolute value."""
    method = max(results, key=lambda m: abs(results[m].coefficient))
    return method, abs(results[method].coefficient)


def rolling_correlation(x: pd.Series, y: pd.Series, window: int) -> pd.Series:
    """Rolling-window Pearson correlation (NaN for the first ``window - 1`` points)."""
    return x.rolling(window=window).corr(y)

"""Lead/lag analysis: cross-correlation function and lagged correlations.

Sign convention (used everywhere in TRACES):
    The value at lag ``k`` is the correlation between ``x[t]`` and ``y[t + k]``.
    A peak at positive ``k`` means **x leads y** by ``k`` observations;
    a peak at negative ``k`` means **y leads x**.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from numpy.typing import ArrayLike, NDArray
from scipy import stats

from .stats import prewhiten as _prewhiten


@dataclass(frozen=True)
class CCFResult:
    """Normalized cross-correlation over lags -max_lag..max_lag."""

    lags: NDArray[np.int64]
    values: NDArray[np.float64]
    n: int
    """Number of observations the CCF was computed from."""
    band: float
    """Half-width of the significance band (Bonferroni across the lags searched)."""
    ar_order: int | None = None
    """AR order used for pre-whitening, or None if not pre-whitened."""

    @property
    def zero_lag(self) -> float:
        return float(self.values[self.lags == 0][0])

    @property
    def peak_index(self) -> int:
        return int(np.nanargmax(np.abs(self.values)))

    @property
    def peak_lag(self) -> int:
        return int(self.lags[self.peak_index])

    @property
    def peak(self) -> float:
        return float(self.values[self.peak_index])

    @property
    def peak_significant(self) -> bool:
        return bool(abs(self.peak) > self.band)

    @property
    def lag_ratio(self) -> float:
        """|CCF(peak lag)| / |CCF(0)|; >= 1 by construction."""
        zero = abs(self.zero_lag)
        return float("inf") if zero == 0 else abs(self.peak) / zero

    def to_frame(self) -> pd.DataFrame:
        return pd.DataFrame({"lag": self.lags, "ccf": self.values})


def cross_correlation(x: ArrayLike, y: ArrayLike, max_lag: int, alpha: float = 0.05) -> CCFResult:
    """Normalized sample cross-correlation function.

    CCF(k) = sum_t (x_t - mean_x)(y_{t+k} - mean_y) / (n * sd_x * sd_y), with
    population standard deviations, so CCF(0) equals the Pearson correlation.

    Only lags within ``[-max_lag, max_lag]`` are computed (clipped to n - 3).
    The significance band is z_{1 - alpha / (2L)} / sqrt(n) for L searched lags,
    which is valid when at least one series is (close to) white noise, e.g.
    after pre-whitening.
    """
    a = np.asarray(x, dtype=float)
    b = np.asarray(y, dtype=float)
    if len(a) != len(b):
        raise ValueError("x and y must have the same length")
    n = len(a)
    max_lag = int(max(0, min(max_lag, n - 3)))
    a = a - a.mean()
    b = b - b.mean()
    denom = n * a.std() * b.std()

    lags = np.arange(-max_lag, max_lag + 1)
    values = np.empty(len(lags))
    for i, k in enumerate(lags):
        if k >= 0:
            values[i] = np.dot(a[: n - k], b[k:])
        else:
            values[i] = np.dot(a[-k:], b[: n + k])
    values = values / denom if denom > 0 else np.full(len(lags), np.nan)

    band = float(stats.norm.ppf(1 - alpha / (2 * len(lags))) / np.sqrt(n))
    return CCFResult(lags=lags, values=values, n=n, band=band)


def prewhitened_cross_correlation(
    x: ArrayLike,
    y: ArrayLike,
    max_lag: int,
    alpha: float = 0.05,
    max_ar_order: int | None = None,
) -> CCFResult:
    """Cross-correlation after pre-whitening both series with x's AR model."""
    fx, fy, order = _prewhiten(x, y, max_ar_order)
    ccf = cross_correlation(fx, fy, max_lag=max_lag, alpha=alpha)
    return CCFResult(ccf.lags, ccf.values, ccf.n, ccf.band, ar_order=order)


def lagged_correlations(x: pd.Series, y: pd.Series, max_lag: int) -> pd.DataFrame:
    """Pearson, Spearman and Kendall correlation of x[t] with y[t + k] for each lag k.

    Unlike :func:`cross_correlation`, each lag uses only the overlapping
    observations and recomputes means, so values are comparable to ordinary
    correlations. Same sign convention (positive lag: x leads y).
    """
    a = np.asarray(x, dtype=float)
    b = np.asarray(y, dtype=float)
    n = len(a)
    max_lag = int(max(0, min(max_lag, n - 3)))
    rows = []
    for k in range(-max_lag, max_lag + 1):
        xa, yb = (a[: n - k], b[k:]) if k >= 0 else (a[-k:], b[: n + k])
        rows.append(
            {
                "lag": k,
                "n": len(xa),
                "pearson": stats.pearsonr(xa, yb).statistic,
                "spearman": stats.spearmanr(xa, yb).statistic,
                "kendall": stats.kendalltau(xa, yb).statistic,
            }
        )
    return pd.DataFrame(rows).set_index("lag")

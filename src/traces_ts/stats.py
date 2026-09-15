"""Statistical helpers: autocorrelation, effective sample size, p-values, AR pre-whitening."""

from __future__ import annotations

import numpy as np
from numpy.typing import ArrayLike, NDArray
from scipy import stats

FloatArray = NDArray[np.float64]


def autocovariance(x: ArrayLike, max_lag: int) -> FloatArray:
    """Biased sample autocovariance for lags 0..max_lag."""
    arr = np.asarray(x, dtype=float)
    arr = arr - arr.mean()
    n = len(arr)
    max_lag = min(max_lag, n - 1)
    return np.array([np.dot(arr[: n - k], arr[k:]) / n for k in range(max_lag + 1)])


def autocorrelation(x: ArrayLike, max_lag: int) -> FloatArray:
    """Sample autocorrelation for lags 0..max_lag (value at lag 0 is 1)."""
    acov = autocovariance(x, max_lag)
    if acov[0] == 0:
        return np.full_like(acov, np.nan)
    return acov / acov[0]


def effective_sample_size(x: ArrayLike, y: ArrayLike) -> float:
    """Effective number of independent observations for correlating two series.

    Pyper & Peterman (1998):
        1/N* = 1/N + (2/N) * sum_{j=1}^{N/5} ((N - j)/N) * rho_xx(j) * rho_yy(j)

    The result is clipped to [3, N]. For white noise N* ~ N; for smooth,
    strongly autocorrelated series N* can be a small fraction of N.
    """
    n = len(np.asarray(x))
    max_j = max(1, n // 5)
    rx = autocorrelation(x, max_j)[1:]
    ry = autocorrelation(y, max_j)[1:]
    j = np.arange(1, len(rx) + 1)
    inv = 1 / n + (2 / n) * np.sum(((n - j) / n) * rx * ry)
    if not np.isfinite(inv) or inv <= 0:
        return float(n)
    return float(np.clip(1 / inv, min(3, n), n))


def correlation_pvalue(r: float, n: float, method: str) -> float:
    """Two-sided p-value for a correlation coefficient given a (possibly effective) sample size.

    Pearson and Spearman use the t approximation with n - 2 degrees of freedom;
    Kendall uses the large-sample normal approximation.
    """
    if not np.isfinite(r) or n <= 2:
        return float("nan")
    if method in {"pearson", "spearman"}:
        if abs(r) >= 1:
            return 0.0
        t = abs(r) * np.sqrt((n - 2) / (1 - r * r))
        return float(2 * stats.t.sf(t, df=n - 2))
    if method == "kendall":
        z = 3 * abs(r) * np.sqrt(n * (n - 1)) / np.sqrt(2 * (2 * n + 1))
        return float(2 * stats.norm.sf(z))
    raise ValueError(f"Unknown correlation method {method!r}")


def fdr_adjust(pvalues: ArrayLike) -> FloatArray:
    """Benjamini-Hochberg adjusted p-values (q-values); NaNs are passed through."""
    p = np.asarray(pvalues, dtype=float)
    out = np.full_like(p, np.nan)
    finite = np.isfinite(p)
    if finite.any():
        out[finite] = stats.false_discovery_control(p[finite], method="bh")
    return out


def fit_ar(x: ArrayLike, max_order: int) -> FloatArray:
    """Fit an AR(p) model with Yule-Walker / Levinson-Durbin, choosing p <= max_order by AIC.

    Returns the AR coefficients phi_1..phi_p (possibly empty).
    """
    arr = np.asarray(x, dtype=float)
    n = len(arr)
    max_order = int(max(0, min(max_order, n - 2)))
    acov = autocovariance(arr, max_order)
    if acov[0] <= 0:
        return np.array([])

    best_phi = np.array([])
    best_aic = n * np.log(acov[0])
    phi = np.array([])
    sigma2 = acov[0]
    for k in range(1, max_order + 1):
        reflection = (acov[k] - np.dot(phi, acov[1:k][::-1])) / sigma2
        phi = np.append(phi - reflection * phi[::-1], reflection)
        sigma2 *= 1 - reflection**2
        if sigma2 <= 0:
            break
        aic = n * np.log(sigma2) + 2 * k
        if aic < best_aic:
            best_aic, best_phi = aic, phi.copy()
    return best_phi


def ar_filter(x: ArrayLike, phi: ArrayLike) -> FloatArray:
    """Residuals e_t = x_t - sum_i phi_i * x_{t-i} of the demeaned series (first p values dropped)."""
    arr = np.asarray(x, dtype=float)
    arr = arr - arr.mean()
    coeffs = np.asarray(phi, dtype=float)
    p = len(coeffs)
    n = len(arr)
    resid = arr[p:].copy()
    for i, c in enumerate(coeffs, start=1):
        resid -= c * arr[p - i : n - i]
    return resid


def prewhiten(
    x: ArrayLike, y: ArrayLike, max_order: int | None = None
) -> tuple[FloatArray, FloatArray, tuple[int, int]]:
    """Double pre-whitening: filter each series with its own AR model.

    Removing each series' autocorrelation makes their residual cross-correlation
    interpretable against white-noise significance bands (Haugh, 1976). Unlike
    single (Box-Jenkins) pre-whitening, the result does not depend on pair order.
    Residuals are aligned on the later start so both have the same length.

    Returns:
        (filtered_x, filtered_y, (ar_order_x, ar_order_y))
    """
    n = len(np.asarray(x))
    if max_order is None:
        max_order = min(10, max(1, n // 5))
    phi_x, phi_y = fit_ar(x, max_order), fit_ar(y, max_order)
    px, py = len(phi_x), len(phi_y)
    start = max(px, py)
    fx = ar_filter(x, phi_x)[start - px :]
    fy = ar_filter(y, phi_y)[start - py :]
    return fx, fy, (px, py)

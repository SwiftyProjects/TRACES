"""Statistical calibration: the v2 safeguards should hold nominal error rates on null data."""

import numpy as np
from scipy import stats

from traces_ts import cross_correlation, effective_sample_size, prewhitened_cross_correlation
from traces_ts.stats import correlation_pvalue

N, MAX_LAG, REPS = 52, 10, 300


def ar1_pair(rng, phi=0.95):
    e = rng.normal(size=(2, N + 200))
    x = np.zeros_like(e)
    for t in range(1, N + 200):
        x[:, t] = phi * x[:, t - 1] + e[:, t]
    return x[0, 200:], x[1, 200:]


def detected(ccf):
    return ccf.peak_significant and ccf.peak_lag != 0 and ccf.lag_ratio >= 1.2


def test_null_error_rates_for_independent_autocorrelated_series():
    rng = np.random.default_rng(2024)
    naive = adjusted = lag_raw = lag_pw = 0
    for _ in range(REPS):
        x, y = ar1_pair(rng)
        r, p = stats.pearsonr(x, y)
        naive += p < 0.05
        adjusted += correlation_pvalue(r, effective_sample_size(x, y), "pearson") < 0.05
        lag_raw += detected(cross_correlation(x, y, MAX_LAG))
        lag_pw += detected(prewhitened_cross_correlation(x, y, MAX_LAG))
    assert naive / REPS > 0.3  # what v1 did
    assert adjusted / REPS < 0.10
    assert lag_raw / REPS > 0.2  # what v1 did
    assert lag_pw / REPS < 0.08

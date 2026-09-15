import numpy as np
import pytest
from scipy import stats

from traces_ts import cross_correlation, lagged_correlations, prewhitened_cross_correlation


def test_zero_lag_equals_pearson(rng):
    x, y = rng.normal(size=(2, 60))
    y = y + x
    ccf = cross_correlation(x, y, max_lag=5)
    assert ccf.zero_lag == pytest.approx(stats.pearsonr(x, y).statistic)
    assert np.all(np.abs(ccf.values) <= 1 + 1e-12)


def test_lags_restricted_to_max_lag(rng):
    x, y = rng.normal(size=(2, 52))
    ccf = cross_correlation(x, y, max_lag=10)
    assert ccf.lags.min() == -10
    assert ccf.lags.max() == 10
    assert abs(ccf.peak_lag) <= 10


def test_max_lag_clipped_for_short_series(rng):
    x, y = rng.normal(size=(2, 8))
    assert cross_correlation(x, y, max_lag=50).lags.max() == 5


@pytest.mark.parametrize("shift", [3, -4])
def test_sign_convention_consistent(rng, shift):
    """Positive lag means x leads y, for the CCF, pre-whitened CCF and lagged correlations."""
    n = 150
    base = rng.normal(size=n + 10)
    x = base[5 : 5 + n]
    y = base[5 - shift : 5 - shift + n] + rng.normal(scale=0.1, size=n)  # y[t] = x[t - shift]
    assert cross_correlation(x, y, 8).peak_lag == shift
    assert prewhitened_cross_correlation(x, y, 8).peak_lag == shift
    assert lagged_correlations(x, y, 8)["pearson"].abs().idxmax() == shift


def test_band_and_significance(rng):
    x = rng.normal(size=100)
    ccf = cross_correlation(x, x, max_lag=5, alpha=0.05)
    assert ccf.band == pytest.approx(stats.norm.ppf(1 - 0.05 / 22) / np.sqrt(100))
    assert ccf.peak_significant
    assert ccf.peak_lag == 0
    assert ccf.lag_ratio == pytest.approx(1.0)


def test_length_mismatch(rng):
    with pytest.raises(ValueError):
        cross_correlation(rng.normal(size=10), rng.normal(size=11), 2)


def test_ccf_frame(rng):
    df = cross_correlation(*rng.normal(size=(2, 30)), max_lag=2).to_frame()
    assert list(df.columns) == ["lag", "ccf"]
    assert len(df) == 5


def test_prewhitened_detection_is_order_independent(rng):
    n = 80
    x = np.cumsum(rng.normal(size=n))
    y = np.cumsum(rng.normal(size=n))
    xy = prewhitened_cross_correlation(x, y, 8)
    yx = prewhitened_cross_correlation(y, x, 8)
    np.testing.assert_allclose(xy.values, yx.values[::-1])
    assert xy.peak_lag == -yx.peak_lag
    assert xy.band == pytest.approx(yx.band)


def test_band_widens_with_leftover_autocorrelation(rng):
    smooth = np.convolve(rng.normal(size=300), np.ones(15) / 15, mode="valid")
    other = np.convolve(rng.normal(size=300), np.ones(15) / 15, mode="valid")
    naive = cross_correlation(smooth, other, 10)
    pw = prewhitened_cross_correlation(smooth, other, 10, max_ar_order=1)
    assert pw.n_band <= pw.n
    assert pw.band >= stats.norm.ppf(1 - 0.05 / 42) / np.sqrt(pw.n) - 1e-12
    assert naive.n_band == naive.n

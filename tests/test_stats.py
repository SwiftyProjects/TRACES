import numpy as np
import pytest
from scipy import stats as sps

from traces_ts.stats import (
    autocorrelation,
    correlation_pvalue,
    effective_sample_size,
    fdr_adjust,
    fit_ar,
    prewhiten,
)


def ar1(rng, n, phi):
    e = rng.normal(size=n + 200)
    x = np.zeros(n + 200)
    for t in range(1, n + 200):
        x[t] = phi * x[t - 1] + e[t]
    return x[200:]


def test_autocorrelation_lag0_is_one(rng):
    acf = autocorrelation(rng.normal(size=100), 5)
    assert acf[0] == pytest.approx(1.0)
    assert np.all(np.abs(acf[1:]) < 0.3)


def test_effective_sample_size_white_noise_near_n(rng):
    x, y = rng.normal(size=(2, 500))
    assert effective_sample_size(x, y) == pytest.approx(500, rel=0.1)


def test_effective_sample_size_shrinks_for_autocorrelated(rng):
    assert effective_sample_size(ar1(rng, 200, 0.9), ar1(rng, 200, 0.9)) < 60


def test_effective_sample_size_clipped():
    x = np.arange(20.0)
    assert 3 <= effective_sample_size(x, x) <= 20


def test_pvalue_matches_scipy_with_full_n(rng):
    x, y = rng.normal(size=(2, 40))
    y = y + 0.4 * x
    for method, fn in (("pearson", sps.pearsonr), ("spearman", sps.spearmanr)):
        res = fn(x, y)
        assert correlation_pvalue(res.statistic, 40, method) == pytest.approx(res.pvalue, rel=1e-6)


def test_kendall_pvalue_large_sample_formula():
    # Var(tau) = 2(2n + 1) / (9n(n - 1)); tau = 0.3, n = 40 gives z = 2.793
    z = 0.3 / np.sqrt(2 * 81 / (9 * 40 * 39))
    assert correlation_pvalue(0.3, 40, "kendall") == pytest.approx(2 * sps.norm.sf(z))
    assert correlation_pvalue(0.3, 40, "kendall") == pytest.approx(0.00522, abs=1e-4)


def test_pvalue_edge_cases():
    assert correlation_pvalue(1.0, 10, "pearson") == 0.0
    assert np.isnan(correlation_pvalue(0.5, 2, "pearson"))
    with pytest.raises(ValueError):
        correlation_pvalue(0.5, 10, "bogus")


def test_fdr_adjust_matches_scipy_and_passes_nan():
    q = fdr_adjust(np.array([0.01, 0.02, np.nan, 0.5]))
    assert np.isnan(q[2])
    np.testing.assert_allclose(q[[0, 1, 3]], sps.false_discovery_control([0.01, 0.02, 0.5]))


def test_fit_ar_recovers_ar1(rng):
    phi = fit_ar(ar1(rng, 2000, 0.7), max_order=5)
    assert len(phi) >= 1
    assert phi[0] == pytest.approx(0.7, abs=0.05)


def test_prewhiten_removes_autocorrelation(rng):
    x = ar1(rng, 500, 0.9)
    fx, fy, order = prewhiten(x, x.copy(), max_order=5)
    assert order >= 1
    assert len(fx) == len(fy) == 500 - order
    assert abs(autocorrelation(fx, 1)[1]) < 0.1

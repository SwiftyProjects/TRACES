import numpy as np
import pandas as pd
import pytest

from traces_ts import AnalysisConfig, analyze, classify_relationship, from_frame, load_data
from traces_ts.analysis import RESULT_COLUMNS


def by_pair(result, a, b):
    t = result.table
    return t[(t.series_1 == a) & (t.series_2 == b)].iloc[0]


def test_config_validation():
    with pytest.raises(ValueError):
        AnalysisConfig(rolling_window=2)
    with pytest.raises(ValueError):
        AnalysisConfig(detrend="log")
    with pytest.raises(ValueError):
        AnalysisConfig(alpha=1.5)
    classic = AnalysisConfig.classic(max_lag=4)
    assert not (classic.prewhiten or classic.fdr_correction or classic.autocorrelation_adjustment)
    assert classic.max_lag == 4


def test_synthetic_relationships(synthetic_frame):
    result = analyze(from_frame(synthetic_frame), AnalysisConfig(max_lag=6))
    assert list(result.table.columns) == list(RESULT_COLUMNS)
    assert len(result.table) == 6

    linear = by_pair(result, "x", "linear")
    assert linear.relationship_type == "linear"
    assert linear.evidence_score > 0.9

    lagged = by_pair(result, "x", "lagged")
    assert lagged.relationship_type == "lagged"
    assert lagged.ccf_peak_lag == 3
    assert lagged.lag_detected

    assert by_pair(result, "x", "noise").relationship_type == "none"


def test_monotonic_nonlinear(rng):
    n = 200
    x = rng.uniform(0, 10, n)
    df = pd.DataFrame({"t": range(n), "x": x, "y": np.exp(x) + rng.normal(scale=0.1, size=n)})
    row = analyze(from_frame(df)).table.iloc[0]
    assert row.relationship_type == "non_linear"
    assert row.spearman > row.pearson


def test_sample_dataset_v2_defaults(sample_path):
    t = analyze(load_data(sample_path)).table
    assert len(t) == 45
    assert t["max_abs_correlation"].is_monotonic_decreasing
    assert (t["ccf_peak_lag"].abs() <= 10).all()
    assert (t["n_effective"] < t["n_obs"]).all()
    assert (t["pearson_p"] >= t["pearson_p_raw"]).all()
    top = t.iloc[0]
    assert (top.series_1, top.series_2, top.relationship_type) == ("Label_3", "Label_10", "linear")


def test_sample_dataset_classic_matches_v1(sample_path):
    """Classic mode keeps v1 p-values and heuristics, so v1's headline counts are reproduced."""
    result = analyze(load_data(sample_path), AnalysisConfig.classic())
    t = result.table
    assert (t["pearson_p"] == t["pearson_p_raw"]).all()
    assert by_pair(result, "Label_3", "Label_10").pearson == pytest.approx(0.998593, abs=1e-6)
    counts = t["relationship_type"].value_counts().to_dict()
    assert counts["linear"] == 4
    assert counts["complex"] == 33


def test_exclusions_and_explicit_pairs(sample_path):
    data = load_data(sample_path)
    excluded = analyze(data, exclude={"Label_1": ["Label_2", "Label_3"]}, keep_details=False)
    assert len(excluded.table) == 43
    assert excluded.details == {}
    assert len(analyze(data, pairs=[("Label_1", "Label_2")]).table) == 1
    with pytest.raises(ValueError, match="unknown series"):
        analyze(data, pairs=[("Label_1", "Nope")])


def test_detrend_difference_drops_row(sample_path):
    result = analyze(load_data(sample_path), AnalysisConfig(detrend="difference"))
    assert result.data.n_observations == 51
    assert (result.table["n_obs"] == 51).all()


def test_constant_series_skipped():
    df = pd.DataFrame(
        {"t": range(20), "a": np.arange(20.0), "b": np.ones(20), "c": np.sin(np.arange(20.0))}
    )
    with pytest.warns(UserWarning, match="constant"):
        result = analyze(df)
    assert len(result.table) == 1
    assert len(result.skipped) == 2


def test_rolling_window_larger_than_data():
    df = pd.DataFrame({"t": range(5), "a": [1.0, 3, 2, 5, 4], "b": [2.0, 1, 4, 3, 5]})
    with pytest.raises(ValueError, match="rolling_window"):
        analyze(df)


def test_result_helpers_and_exports(sample_path, tmp_path):
    result = analyze(load_data(sample_path))
    assert result.pair("Label_10", "Label_3") is result.pair("Label_3", "Label_10")
    with pytest.raises(KeyError):
        result.pair("Label_1", "missing")
    assert len(result.top(5)) == 5
    assert set(result.by_type("linear")["relationship_type"]) == {"linear"}
    csv = result.to_csv(tmp_path / "out" / "r.csv")
    xlsx = result.to_excel(tmp_path / "out" / "r.xlsx")
    assert pd.read_csv(csv).shape == result.table.shape
    assert set(pd.ExcelFile(xlsx).sheet_names) == {"results", "summary", "config"}
    assert repr(result).startswith("AnalysisResult(n_pairs=45")


def test_classification_rules():
    cfg = AnalysisConfig()
    base = {
        "kendall": 0.5,
        "rolling_std": 0.05,
        "lag_detected": False,
        "ccf_peak": 0.0,
        "config": cfg,
    }

    def kind(**kw):
        return classify_relationship(**{**base, **kw}).relationship_type

    assert kind(pearson=0.9, spearman=0.88, significant_methods=3) == "linear"
    assert kind(pearson=0.5, spearman=0.8, significant_methods=2) == "non_linear"
    assert kind(pearson=0.9, spearman=0.9, significant_methods=0) == "none"
    assert kind(pearson=0.1, spearman=0.1, kendall=0.1, significant_methods=3) == "none"
    assert kind(pearson=0.7, spearman=0.6, significant_methods=3, rolling_std=0.4) == "complex"

    lag = classify_relationship(
        **{
            **base,
            "pearson": 0.1,
            "spearman": 0.1,
            "significant_methods": 0,
            "lag_detected": True,
            "ccf_peak": -0.6,
        }
    )
    assert lag.relationship_type == "lagged"
    assert lag.recommended_methods == ("ccf",)
    assert lag.evidence_score == pytest.approx(0.6)

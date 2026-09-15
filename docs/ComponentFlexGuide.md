# TRACES (Time-series Relationship Analysis with Comprehensive Evaluation Suite)

---

# **Component Flexibility Guide**

What you can safely change, what to change with care, and what forms the statistical core.

## GREEN zone: tune freely for your data

| Setting | Where | Guidance |
|---|---|---|
| `rolling_window` | `AnalysisConfig` | Roughly one seasonal cycle (e.g. 12 for monthly, 52 for weekly data); must not exceed the series length |
| `max_lag` | `AnalysisConfig` | Longest lead/lag that is plausible in your domain; more lags widen the significance band |
| `alpha` | `AnalysisConfig` | 0.05 by default; 0.01 for stricter screening |
| `min_correlation` | `AnalysisConfig` | Minimum practically meaningful strength |
| `detrend` | `AnalysisConfig` | `"difference"` for random-walk-like series, `"linear"` for trending series |
| Input handling | `load_data(time_column=, sheet_name=, missing=)` | Match your file |
| Exclusions | `analyze(exclude=...)` or `pairs=` | Parent/child or otherwise uninteresting pairs |
| Plot styling | `traces_ts.viz` arguments (`top`, `figsize`, `value`) | Every function returns a Figure you can restyle |
| Outputs | `to_csv`, `to_excel`, `render_markdown`, `save_figures` | Choose what to export |

## YELLOW zone: modify with caution

These change what the results mean. Document any changes alongside your results.

| Setting | Default | Effect |
|---|---|---|
| `autocorrelation_adjustment` | `True` | Disabling makes p-values assume independent observations; expect many false positives on smooth series |
| `fdr_correction` | `True` | Disabling increases false discoveries when analysing many pairs |
| `prewhiten` | `True` | Disabling makes the lag band invalid for autocorrelated series (30-50% false lags in simulation) |
| `max_ar_order` | `min(10, n/5)` | Higher orders whiten better but cost observations |
| `linear_max_rank_gap` | 0.1 | Maximum \|Pearson - Spearman\| for `linear` |
| `linear_max_rolling_std` | 0.2 | Maximum rolling-correlation variability for `linear` |
| `nonlinear_min_rank_gain` | 0.2 | Minimum \|Spearman\| - \|Pearson\| for `non_linear` |
| `lag_min_ratio` | 1.2 | How much the lagged peak must exceed the zero-lag CCF |

`AnalysisConfig.classic()` switches off the first three for comparison with TRACES v1.

## RED zone: core framework

Change only with tests and a clear statistical rationale (see [Formulae](Formulae.md)).

| Component | Module |
|---|---|
| Correlation coefficients and raw p-values | `traces_ts.correlation` |
| Effective sample size, adjusted p-values, FDR, AR fitting and pre-whitening | `traces_ts.stats` |
| CCF normalization, lag sign convention and significance bands | `traces_ts.lags` |
| Classification rule order and evidence score | `traces_ts.classify` |
| Data validation and pair generation | `traces_ts.io` |
| Pipeline orchestration and result schema | `traces_ts.analysis` |

The calibration tests in `tests/test_calibration.py` guard the statistical behaviour; run
`uv run pytest` after any change here.

## Critical requirements

1. **Data structure**: one row per time point at regular intervals, ordered in time, numeric series
   and unique series names.
2. **Sample size**: at least 3 observations (practically, 30 or more), `rolling_window` no larger than
   the series length, and `max_lag` well below the series length.
3. **Missing data**: decide on a policy explicitly (`raise`, `drop`, `interpolate`). Dropping rows breaks
   regular spacing and affects lag interpretation.

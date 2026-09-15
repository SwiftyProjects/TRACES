# Changelog

All notable changes to TRACES are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses
[Semantic Versioning](https://semver.org/).

## [2.0.0] - 2026-09-15

A full modernization. **Results differ from v1**: several v1 calculations were wrong, and the
default significance tests now account for autocorrelation and multiple testing.

### Added

- `traces_ts` Python package (`pip install -e .` / `uv sync`) with a documented public API:
  `load_data`, `analyze`, `AnalysisConfig`, `AnalysisResult`, `cross_correlation`,
  `prewhitened_cross_correlation`, `lagged_correlations`, `effective_sample_size` and more.
- `traces analyze` command-line interface writing CSV, Excel, a Markdown report and figures.
- Autocorrelation-adjusted p-values using the effective sample size (Pyper & Peterman, 1998).
- Benjamini-Hochberg false discovery rate correction across pairs.
- Double AR pre-whitening before lag detection, with Bonferroni significance bands across lags.
- `none` relationship type and a documented evidence score.
- Detrending options: `none`, `linear`, `difference`.
- CSV input, configurable time column, date parsing and an explicit missing-value policy.
- Excel export with results, summary and config sheets; Markdown reports.
- New plots: per-pair CCF with significance band, rolling correlation; relationship matrix now
  covers every series.
- `AnalysisConfig.classic()` for v1-style results without the new safeguards.
- High-persistence warning in reports for random-walk-like series.
- pytest suite (58 tests, including statistical calibration), notebook execution test and
  GitHub Actions CI on Python 3.11-3.14 (Linux, Windows, macOS) and lowest supported dependencies.
- `pyproject.toml`, `uv.lock`, `CITATION.cff`, `scripts/generate_examples.py`.

### Fixed

- **CCF optimal lag ignored `max_lag`.** v1 searched all lags before filtering, reporting lags of
  11-12 with `max_lag=10`.
- **Contradictory lag signs.** v1's CCF and time-delayed correlations reported opposite signs for
  the same lead. Everywhere now: positive lag means `series_1` leads `series_2`.
- **CCF was not normalized.** v1 values were `r x (n - 1)` (e.g. 50.9), not a percentage as
  documented. CCF(0) now equals Pearson r.
- **Hard-coded `Time` column.** The first column is now the time column, as documented.
- **Missing values were not handled** despite the documentation; they silently produced NaN results.
- **Method-performance legend** showed `(count, method)` labels.
- The "confidence" score was unrelated to the classification and ignored the lag analysis; it is
  replaced by the documented `evidence_score`.
- The relationship matrix no longer requires an "even number of top pairs".

### Changed

- **Default statistics** (see above). In simulations with independent autocorrelated series, naive
  tests flagged 52-67% of pairs as significant; v2 holds 6% for stationary series.
- Analysis logic moved out of the notebook into `src/traces_ts`; the notebook is a thin walkthrough.
- Results use snake_case columns (`series_1`, `relationship_type`, `evidence_score`, `pearson_p`, ...).
- `environment.yml` uses conda-forge only (the Anaconda `defaults` channel has commercial terms)
  and installs the package; `pyproject.toml` is the source of truth for dependencies.
- Supported Python: 3.11-3.14 (tested with NumPy 2.5, pandas 3.0, SciPy 1.18, matplotlib 3.11).
- Example outputs are generated from real runs by `scripts/generate_examples.py`.

### Removed

- Hand-written example outputs (`docs/examples/outputs/step*.txt`) that did not match the code.
- Unused `black` and `flake8` dependencies (replaced by `ruff`).

### Migrating from v1

| v1 | v2 |
|---|---|
| Edit `CONFIG` dict in cell 1 | `AnalysisConfig(rolling_window=..., max_lag=..., alpha=...)` |
| `PARENT_CHILD_MAPPING` | `analyze(data, exclude={"parent": ["child", ...]})` |
| `load_and_prepare_data(path)` | `data = load_data(path)` |
| `run_full_analysis(df, valid_pairs)` | `result = analyze(data)` |
| `final_results` DataFrame | `result.table` |
| `Series 1`, `Relationship Type`, `Confidence`, `Max CCF`, `Optimal Lag` | `series_1`, `relationship_type`, `evidence_score`, `ccf_peak`, `ccf_peak_lag` |
| `significance_level` | `alpha` |
| v1-like statistics | `AnalysisConfig.classic()` or `traces analyze --classic` |

## [1.0.0] - 2024-11-29

Initial release: Jupyter notebook implementation with Pearson, Spearman, Kendall, CCF and rolling
correlation analysis, relationship classification and visualization suite.

[2.0.0]: https://github.com/SwiftyProjects/TRACES/compare/v1.0.0...v2.0.0
[1.0.0]: https://github.com/SwiftyProjects/TRACES/releases/tag/v1.0.0

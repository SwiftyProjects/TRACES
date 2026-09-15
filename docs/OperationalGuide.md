# TRACES (Time-series Relationship Analysis with Comprehensive Evaluation Suite)

---

# **Operational Guide**

## 1. Installation

TRACES is a standard Python package (`pyproject.toml`), so any environment manager works.

| Tool | Commands |
|---|---|
| **uv** (recommended) | `uv sync --all-extras` then prefix commands with `uv run` |
| **venv + pip** | `python -m venv .venv`, activate it, `pip install -e ".[notebook]"` |
| **conda / mamba** | `conda env create -f environment.yml` then `conda activate traces-env` |

The `notebook` extra adds JupyterLab. For development, `uv sync --all-extras` also installs the
`dev` group (pytest, nbmake, ruff); with pip use `pip install --group dev` (pip 25.1+).

## 2. Three ways to run an analysis

### A. Notebook (`notebooks/TRACES_ES.ipynb`)

Run all cells top to bottom. Every step depends only on Step 1, so after changing settings in
Step 1, re-run from Step 1 (no kernel restart needed).

| Step | Purpose | Edit? |
|---|---|---|
| 1. Setup and data loading | Choose `DATA_FILE`, `EXCLUDE`, `CONFIG`; inspect series and persistence | **Yes** |
| 2. Run the analysis | `analyze(...)` and headline summary | No |
| 3. Correlations and significance | Coefficients, raw vs adjusted significance, comparison plot | No |
| 4. Lead/lag analysis | Detected lead/lags, CCF overview, per-pair CCF | No |
| 5. Relationship classification | Types, evidence scores, matrix, method and rolling plots | No |
| 6. Export and v1 comparison | Write `results/`, compare with `AnalysisConfig.classic()` | Optional |

### B. Command line

```bash
traces analyze PATH [options]
```

| Option | Default | Description |
|---|---|---|
| `-o, --out DIR` | `results` | Output directory |
| `--time-column NAME` | first column | Time column |
| `--sheet NAME_OR_INDEX` | `0` | Excel worksheet |
| `--missing {raise,drop,interpolate}` | `raise` | Missing-value policy |
| `--exclude PARENT=CHILD[,CHILD]` | none | Exclude parent/child pairs (repeatable) |
| `--rolling-window N` | 12 | Rolling window |
| `--max-lag N` | 10 | Lag search range |
| `--alpha A` | 0.05 | Significance level |
| `--min-correlation R` | 0.3 | Minimum strength |
| `--detrend {none,linear,difference}` | `none` | Pre-processing |
| `--no-autocorrelation-adjustment`, `--no-fdr`, `--no-prewhiten` | | Disable one safeguard |
| `--classic` | | Disable all three (v1-style) |
| `--top N` | 10 | Pairs listed in the report |
| `--no-figures`, `--no-excel` | | Skip those outputs |

Outputs: `results.csv`, `results.xlsx` (results, summary, config sheets), `report.md` and
`figures/*.png`. Exit code 2 signals invalid input.

### C. Python API

```python
from traces_ts import AnalysisConfig, analyze, load_data, render_markdown, viz

data = load_data("my_data.csv", time_column="Date", missing="interpolate")
config = AnalysisConfig(max_lag=12, detrend="difference")
result = analyze(data, config, exclude={"Total": ["North", "South"]})

result.table  # one row per pair
result.top(10)  # by evidence score
result.by_type("lagged")  # filter by relationship type
result.pair("North", "West").ccf  # CCFResult with lags, values, band
result.summary()  # dict of headline statistics

fig = viz.plot_pair_ccf(result, "North", "West")
result.to_excel("results/my_results.xlsx")
```

Lower-level building blocks (`basic_correlations`, `cross_correlation`,
`prewhitened_cross_correlation`, `lagged_correlations`, `effective_sample_size`,
`classify_relationship`) can be used on any pair of arrays.

## 3. Results table columns

| Column | Meaning |
|---|---|
| `series_1`, `series_2` | The pair |
| `relationship_type` | `linear`, `non_linear`, `lagged`, `complex`, `none` |
| `evidence_score` | 0-1 ranking of strength x statistical support |
| `recommended_methods` | Methods suited to the relationship type |
| `strongest_method`, `max_abs_correlation` | Method with the largest absolute coefficient |
| `pearson`, `spearman`, `kendall` | Coefficients |
| `*_p` | Final p-values (autocorrelation-adjusted, FDR-corrected as configured) |
| `*_p_raw` | Naive p-values assuming independent observations |
| `significant_methods` | Number of methods with `*_p < alpha` |
| `n_obs`, `n_effective` | Observations and effective sample size |
| `rolling_mean`, `rolling_std` | Rolling correlation level and stability |
| `ccf_zero_lag`, `ccf_peak`, `ccf_peak_lag` | Detection CCF at lag 0 and at its peak (positive lag: series_1 leads) |
| `ccf_band`, `ccf_peak_significant` | Significance band and whether the peak exceeds it |
| `lag_ratio`, `lag_detected` | Peak / zero-lag ratio and final lead/lag decision |

## 4. Interpreting results

- **Start with `relationship_type` and `evidence_score`**, then check `n_effective`: a value far below
  `n_obs` means the series are smooth and there is less independent evidence than the row count suggests.
- **Compare `*_p_raw` with `*_p`.** Pairs significant only under raw p-values are likely artifacts
  of shared trends or autocorrelation.
- **Heed the persistence note** in reports. For random-walk-like data, re-run with
  `detrend="difference"`; relationships that survive are much more credible.
- **Lagged relationships** are hypotheses: inspect `viz.plot_pair_ccf` and consider domain plausibility.
- **`complex`** usually means the strength changes over time; look at `viz.plot_rolling_correlation`.

## 5. Performance

Pairs grow quadratically: 10 series give 45 pairs, 100 series give 4,950. Analysis of the 45 sample
pairs takes well under a second. For thousands of pairs pass `keep_details=False` to save memory,
and use `pairs=` to analyse a subset. `lagged_correlations` (all three methods at every lag) is not
run by `analyze`; call it on demand for specific pairs.

## 6. Development workflow

```bash
uv run pytest                              # unit and calibration tests
uv run pytest --nbmake notebooks           # execute the notebook
uv run ruff check . && uv run ruff format .
uv run python scripts/generate_examples.py # refresh docs/examples
```

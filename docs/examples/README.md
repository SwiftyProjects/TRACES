# TRACES (Time-series Relationship Analysis with Comprehensive Evaluation Suite)

---

# **Example Outputs**

Everything in this directory is generated from the bundled sample datasets by

```bash
uv run python scripts/generate_examples.py
```

so it always matches the current code.

```
docs/examples/
├── README.md                       # this file
├── outputs/
│   ├── report_A1.md                # full report, dataset A1, v2 defaults
│   ├── report_A1_classic.md        # same data with AnalysisConfig.classic() (v1-style statistics)
│   ├── classic_vs_v2_A1.csv        # relationship-type counts, classic vs v2
│   ├── results_A1.csv              # full results table, dataset A1
│   └── report_B1.md                # full report, dataset B1
└── visualizations/                 # dataset A1, v2 defaults
    ├── correlation_comparison.png  # Pearson / Spearman / Kendall for the strongest pairs
    ├── relationship_matrix.png     # all pairs: type and evidence score
    ├── method_performance.png      # strongest method by relationship type
    ├── ccf_analysis.png            # peak pre-whitened CCF vs lag
    └── ccf_<pair>.png              # per-pair CCF with significance band (top pairs)
```

## Source datasets

`data/examples/TRACES_sample_52x10_dataset_A1.xlsx` and `..._B1.xlsx`: 52 weekly time points,
a `Time` column and 10 series (`Label_1` to `Label_10`).

## Key results for dataset A1

| Relationship type | Classic (v1-style) | v2 default |
|---|---|---|
| linear | 4 | 4 |
| non_linear | 0 | 0 |
| lagged | 7 | 0 |
| complex | 33 | 5 |
| none | 1 | 36 |

The same four linear relationships (`Label_3`/`Label_10`, `Label_4`/`Label_9`, `Label_2`/`Label_9`,
`Label_2`/`Label_4`) are found by both classic and v2 statistics, and with linear detrending. Three of
them also hold for first differences (`detrend="difference"`), where `Label_7`/`Label_8` replaces
`Label_2`/`Label_9`, so those three are the most robust findings in this dataset. Most other
"relationships" reported by v1-style statistics do not survive once autocorrelation is taken into
account: the series are very smooth (lag-1 autocorrelation 0.95-1.00), so their 52 points carry the
information of only about 9 independent observations. The seven v1 "lagged" pairs were artifacts of
the unrestricted lag search and missing pre-whitening.

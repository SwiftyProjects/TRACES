# TRACES (Time-series Relationship Analysis with Comprehensive Evaluation Suite)

---

# TRACES Example Outputs README

This directory contains example outputs generated using the TRACES analytical framework. All examples are generated using the primary sample dataset `TRACES_sample_52x10_dataset_A1.xlsx`.

---

TRACES/
├── data
│   └── examples
│       ├── TRACES_sample_52x10_dataset_A1.xlsx		# Link to reference source data in /data/examples/
│       └── TRACES_sample_52x10_dataset_B1.xlsx		# bonus time-series dataset to try, example outputs not provided
├── docs
│   ├── ComponentFlexGuide.md
│   ├── Formulae.md
│   ├── OperationalGuide.md
│   └── examples
│       ├── README.md				        # **THIS FILE**
│       ├── outputs
│       │   ├── step1_setup.txt			    # Initial data loading results
│       │   ├── step2_correlations.txt		# Core correlation analysis
│       │   ├── step3_advanced.txt		    # Advanced correlation methods
│       │   ├── step4_framework.txt		    # Analysis framework results
│       │   └── step6_full_analysis.txt		# Complete dataset analysis
│       └── visualizations
│           ├── ccf_analysis.png		    # CCF Analysis scatter plot
│           ├── correlation_comparison.png	# Method comparison bar plot
│           ├── method_performance.png		# Performance by relationship type
│           └── relationship_matrix.png		# Confidence score matrix

---

# TRACES Example Outputs

This directory contains example outputs generated using the TRACES analytical framework. All examples are generated using the primary sample dataset `TRACES_sample_52x10_dataset_A1.xlsx`.

## Source Dataset Reference
Primary dataset: `/data/examples/TRACES_sample_52x10_dataset_A1.xlsx`
- 52 time points (weekly intervals)
- 11 columns total:
  - Time column
  - 10 time series (Label_1 through Label_10)
- Used to generate all example outputs shown here

Note: An additional sample dataset (`TRACES_sample_52x10_dataset_B1.xlsx`) is provided in the same directory for users to practice with different time series data.

## Directory Contents

### Output Files (`/outputs/`)

Step-by-step analysis results from the TRACES notebook:
1. `step1_setup.txt` - Initial data loading and validation
2. `step2_correlations.txt` - Basic correlation analysis
3. `step3_advanced.txt` - Advanced correlation methods
4. `step4_framework.txt` - Analysis framework results
5. `step6_full_analysis.txt` - Complete dataset analysis

### Visualizations (`/visualizations/`)

Four key visualization outputs:

1. `ccf_analysis.png` - Cross-correlation function analysis scatter plot
   - Shows relationship between maximum correlation and optimal lag
   - Color indicates confidence score

2. `correlation_comparison.png` - Method comparison bar plot
   - Compares Pearson, Spearman, and Kendall methods
   - Shows relative performance across pairs

3. `method_performance.png` - Performance by relationship type
   - Distribution of best methods
   - Breakdown by relationship classification

4. `relationship_matrix.png` - Confidence score matrix
   - Heatmap of relationship types
   - Color intensity shows confidence level

## Key Analysis Results

1. **Relationship Types Found**
   - Complex: 33 pairs
   - Lagged: 7 pairs
   - Linear: 4 pairs
   - Non-linear: 1 pair

2. **Correlation Strength Distribution**
   - Strong correlations (>0.7): 15 pairs
   - Moderate correlations (0.3-0.7): 26 pairs
   - Weak correlations (<0.3): 4 pairs

3. **Method Performance**
   - Primary methods: CCF+Spearman (complex relationships), Pearson (linear)
   - Overall mean confidence score: 0.582
   - Highest confidence: 0.999 (Label_3 vs Label_10)

## Usage Notes

- All outputs are reproducible using the primary sample dataset
- Examples exhibit the dynamic range of TRACES capabilities
- Text outputs provide detailed analysis at each step
- Visualizations show key relationships and patterns
- Reference the `OperationalGuide.md` for execution details
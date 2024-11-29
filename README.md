# TRACES (Time-series Relationship Analysis with Comprehensive Evaluation Suite)

---

_A Hierarchical Multi-Method Time Series Correlation Analyzer_

## Overview

TRACES is a comprehensive framework for analyzing relationships between time series data using multiple correlation methods. It automatically determines the most appropriate correlation method(s) for each pair of series and provides detailed visualizations and analysis.

## Key Features

- Multi-method correlation analysis
  - Pearson correlation
  - Spearman rank correlation
  - Kendall's Tau
  - Cross-Correlation Function (CCF)
  - Rolling window correlations
- Automatic relationship type classification
  - **Linear** relationships
  - **Non-linear** relationships
  - **Lagged** relationships
  - **Complex** relationships
- Confidence scoring system
- Advanced visualization suite
- Comprehensive statistical testing
- Parent-child relationship handling

## Input Requirements

- Excel file (.xlsx)
- First row: Column headers (series labels)
- First column: Time intervals
- Additional columns: Time series data
- Minimum 3 data points per series
- Numeric data only (except time labels)

## Analysis Pipeline

1. **Setup and Configuration**
   - Environment initialization
   - Data loading and validation
   - Parent-child relationship definition

2. **Core Correlation Analysis**
   - Basic correlation calculations
   - Significance testing
   - Method comparison framework

3. **Advanced Analysis**
   - Cross-correlation analysis
   - Time-delayed correlations
   - Rolling window analysis

4. **Relationship Classification**
   - Type determination
   - Confidence scoring
   - Method recommendations

5. **Visualization**
   - Correlation method comparisons
   - Relationship matrix heatmaps
   - Method performance analysis
   - CCF and lag pattern visualization

6. **Results Processing**
   - Comprehensive summary statistics
   - Grouped relationship analysis
   - Strength distribution reports

## Output Components

1. **Correlation Analysis**
   - Basic correlations with significance tests
   - Time-delayed correlation patterns
   - Rolling correlation trends
   - Cross-correlation results

2. **Classification Results**
   - Relationship type identification
   - Confidence scores
   - Method recommendations
   - Supporting metrics

3. **Visualization Suite**
   - Interactive correlation comparisons
   - Relationship type matrix (optimized for top $N$ even-numbered pairs)
     - Includes strategic NaN visualization for unpaired relationships
     - Highlights strongest relationship patterns effectively
   - Method performance charts
   - CCF pattern analysis

4. **Summary Statistics**
   - Relationship type distribution
   - Correlation strength metrics
   - Confidence score analysis
   - Method effectiveness summary

## Technical Dependencies

- Python 3.x
- Core libraries:
  - pandas
  - numpy
  - scipy
  - matplotlib
  - seaborn

## Performance Considerations

- Optimized for datasets with up to 1000's of pair comparisons
- Automatic handling of missing values
- Efficient parent-child relationship exclusion
- Scalable visualization components
# TRACES
## Time-series Relationship Analysis with Comprehensive Evaluation Suite

A specialized Python framework for multi-method time series correlation analysis with automatic method optimization.

### Overview
TRACES automatically analyzes relationships between time series data using multiple correlation methods (Pearson, Spearman, Kendall, CCF) and determines the most appropriate method(s) for each pair.

### Key Features
- Automatic detection of relationship types (linear, non-linear, lagged, complex)
- Handles hierarchical data structures (parent-child relationships)
- Comprehensive visualization suite
- Multi-method correlation analysis
- Statistical significance testing

### Requirements
- Python 3.8+
- pandas
- numpy
- scipy
- matplotlib
- seaborn

### Input Data Format
- Excel file (.xlsx)
- First row: Column headers (series names)
- First column: Time intervals
- Additional columns: Time series data

### Quick Start
```python

# Example usage
import pandas as pd
from traces import analyze_full_dataset

# Load your data
df = pd.read_excel('your_data.xlsx')

# Run analysis
results = analyze_full_dataset(df, valid_pairs)

# View results
print(results.sort_values('Abs_Max_Corr', ascending=False))

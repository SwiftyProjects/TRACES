# TRACES (Time-series Relationship Analysis with Comprehensive Evaluation Suite)

_A Hierarchical Multi-Method Time Series Correlation Analyzer_

---

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
![Python](https://img.shields.io/badge/python-3.12-blue.svg)
![Jupyter](https://img.shields.io/badge/Jupyter-Lab-orange.svg)
![Pandas](https://img.shields.io/badge/pandas-2.2.0-darkblue.svg)
![NumPy](https://img.shields.io/badge/numpy-2.1.0-lightblue.svg)

---

## Overview

TRACES is a comprehensive framework for analyzing relationships between time series data using multiple correlation methods. It automatically determines the most appropriate correlation method(s) for each pair of series and provides detailed visualizations and analysis.

## Quick Start

1. **Clone the repository:**
   ```bash
   git clone https://github.com/SwiftyProjects/TRACES.git
   cd TRACES
   ```

2. **Create the conda environment:**
   ```bash
   conda env create -f environment.yml
   conda activate traces-env
   ```

3. **Launch Jupyter Lab:**
   ```bash
   jupyter lab
   ```

4. **Open the notebook:**
   - Navigate to `notebooks/TRACES_ES.ipynb`
   - Run the example analysis using provided sample data

## Example Outputs

See `/docs/examples/` for complete example outputs including:
- Visualizations of correlation analyses
- Detailed results from each analysis step
- Sample data processing demonstrations

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

## Documentation

- **User Guides:**
  - [Operational Guide](docs/OperationalGuide.md)
  - [Component Flexibility Guide](docs/ComponentFlexGuide.md)
  - [Mathematical Formulae](docs/Formulae.md)

- **Examples:**
  - Complete example outputs in [/docs/examples/](docs/examples/)
  - Sample datasets in [/data/examples/](data/examples/)

## Requirements

- Python 3.12+
- Conda or Miniconda
- See `environment.yml` for complete dependency list

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Citation

If you use TRACES in your research, please cite:
```bibtex
@software{TRACES2024,
  author = {SwiftyProjects},
  title = {TRACES: Time-series Relationship Analysis with Comprehensive Evaluation Suite},
  year = {2024},
  publisher = {GitHub},
  url = {https://github.com/SwiftyProjects/TRACES}
}
```
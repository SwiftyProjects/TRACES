"""TRACES: Time-series Relationship Analysis with Comprehensive Evaluation Suite.

Quick start::

    from traces_ts import AnalysisConfig, analyze, load_data

    data = load_data("data/examples/TRACES_sample_52x10_dataset_A1.xlsx")
    result = analyze(data, AnalysisConfig(max_lag=8))
    result.top(10)

Plotting lives in :mod:`traces_ts.viz`.
"""

from importlib.metadata import PackageNotFoundError, version

from .analysis import AnalysisResult, PairDetail, analyze
from .classify import RELATIONSHIP_TYPES, classify_relationship
from .config import AnalysisConfig
from .correlation import basic_correlations, rolling_correlation
from .io import TimeSeriesData, from_frame, generate_pairs, load_data
from .lags import (
    CCFResult,
    cross_correlation,
    lagged_correlations,
    prewhitened_cross_correlation,
)
from .report import render_markdown, summary_statistics
from .stats import effective_sample_size

try:
    __version__ = version("traces-ts")
except PackageNotFoundError:  # pragma: no cover - running from a source tree
    __version__ = "0.0.0+unknown"

__all__ = [
    "RELATIONSHIP_TYPES",
    "AnalysisConfig",
    "AnalysisResult",
    "CCFResult",
    "PairDetail",
    "TimeSeriesData",
    "__version__",
    "analyze",
    "basic_correlations",
    "classify_relationship",
    "cross_correlation",
    "effective_sample_size",
    "from_frame",
    "generate_pairs",
    "lagged_correlations",
    "load_data",
    "prewhitened_cross_correlation",
    "render_markdown",
    "rolling_correlation",
    "summary_statistics",
]

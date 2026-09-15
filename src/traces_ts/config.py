"""Analysis configuration for TRACES."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Literal

Detrend = Literal["none", "linear", "difference"]
DETREND_OPTIONS: tuple[str, ...] = ("none", "linear", "difference")


@dataclass(frozen=True)
class AnalysisConfig:
    """Parameters controlling a TRACES analysis run.

    Green zone (safe to tune for your data):
        rolling_window, max_lag, alpha, min_correlation, detrend

    Statistical safeguards (on by default; disable only to reproduce v1-style results):
        autocorrelation_adjustment, fdr_correction, prewhiten

    Yellow zone (classification heuristics; change with care):
        linear_max_rank_gap, linear_max_rolling_std, nonlinear_min_rank_gain, lag_min_ratio
    """

    rolling_window: int = 12
    """Window length (observations) for rolling Pearson correlation."""

    max_lag: int = 10
    """Largest lead/lag (in observations, both directions) searched by the CCF."""

    alpha: float = 0.05
    """Significance level for correlation tests and CCF bands."""

    min_correlation: float = 0.3
    """Minimum max(|r|, |rho|, |tau|) for a pair to be classified as related."""

    detrend: Detrend = "none"
    """Pre-processing applied to every series: 'none', 'linear' or 'difference'."""

    autocorrelation_adjustment: bool = True
    """Use an effective sample size (Pyper & Peterman, 1998) for p-values."""

    fdr_correction: bool = True
    """Apply Benjamini-Hochberg FDR control across all pairs, per method."""

    prewhiten: bool = True
    """Pre-whiten each series with its own AR model before lag detection."""

    max_ar_order: int | None = None
    """Upper bound for the pre-whitening AR order (default: min(10, n // 5))."""

    linear_max_rank_gap: float = 0.1
    """Linear if |pearson - spearman| is below this ..."""

    linear_max_rolling_std: float = 0.2
    """... and the rolling correlation is this stable."""

    nonlinear_min_rank_gain: float = 0.2
    """Non-linear (monotonic) if |spearman| - |pearson| exceeds this."""

    lag_min_ratio: float = 1.2
    """Lagged if |CCF at best lag| / |CCF at lag 0| is at least this."""

    def __post_init__(self) -> None:
        if self.rolling_window < 3:
            raise ValueError("rolling_window must be at least 3")
        if self.max_lag < 0:
            raise ValueError("max_lag must be non-negative")
        if not 0 < self.alpha < 1:
            raise ValueError("alpha must be between 0 and 1")
        if not 0 <= self.min_correlation <= 1:
            raise ValueError("min_correlation must be between 0 and 1")
        if self.detrend not in DETREND_OPTIONS:
            raise ValueError(f"detrend must be one of {DETREND_OPTIONS}, got {self.detrend!r}")
        if self.max_ar_order is not None and self.max_ar_order < 0:
            raise ValueError("max_ar_order must be non-negative")
        if self.lag_min_ratio < 1:
            raise ValueError("lag_min_ratio must be at least 1")

    @classmethod
    def classic(cls, **overrides: Any) -> AnalysisConfig:
        """Configuration without the v2 statistical safeguards (closest to TRACES v1).

        Lag-range, lag-sign and CCF-scaling fixes still apply.
        """
        params: dict[str, Any] = {
            "autocorrelation_adjustment": False,
            "fdr_correction": False,
            "prewhiten": False,
        }
        params.update(overrides)
        return cls(**params)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

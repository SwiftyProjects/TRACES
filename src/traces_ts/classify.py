"""Relationship classification and evidence scoring."""

from __future__ import annotations

from dataclasses import dataclass

from .config import AnalysisConfig

RELATIONSHIP_TYPES: tuple[str, ...] = ("linear", "non_linear", "lagged", "complex", "none")

RECOMMENDED_METHODS: dict[str, tuple[str, ...]] = {
    "linear": ("pearson",),
    "non_linear": ("spearman", "kendall"),
    "lagged": ("ccf",),
    "complex": ("ccf", "spearman"),
    "none": (),
}


@dataclass(frozen=True)
class Classification:
    relationship_type: str
    recommended_methods: tuple[str, ...]
    evidence_score: float


def classify_relationship(
    *,
    pearson: float,
    spearman: float,
    kendall: float,
    significant_methods: int,
    rolling_std: float,
    lag_detected: bool,
    ccf_peak: float,
    config: AnalysisConfig,
) -> Classification:
    """Classify a pair's relationship.

    Rules, evaluated in order:

    1. **none**    - no method significant, or max |coefficient| < ``min_correlation``,
                     and no significant lead/lag.
    2. **linear**  - |pearson - spearman| < ``linear_max_rank_gap`` and the rolling
                     correlation std < ``linear_max_rolling_std``.
    3. **non_linear** - |spearman| - |pearson| > ``nonlinear_min_rank_gain``
                     (monotonic but not straight-line).
    4. **lagged**  - significant CCF peak at a non-zero lag, at least
                     ``lag_min_ratio`` times the zero-lag CCF.
    5. **complex** - related, but none of the above (e.g. time-varying strength).

    Evidence score (0-1):
        max( (S / 3) * max(|r|, |rho|, |tau|),  1[lag detected] * |CCF peak| )
    where S is the number of methods significant after the configured corrections.
    """
    max_abs = max(abs(pearson), abs(spearman), abs(kendall))
    related = significant_methods > 0 and max_abs >= config.min_correlation

    if not related:
        rel_type = "lagged" if lag_detected else "none"
    elif (
        abs(pearson - spearman) < config.linear_max_rank_gap
        and rolling_std < config.linear_max_rolling_std
    ):
        rel_type = "linear"
    elif abs(spearman) - abs(pearson) > config.nonlinear_min_rank_gain:
        rel_type = "non_linear"
    elif lag_detected:
        rel_type = "lagged"
    else:
        rel_type = "complex"

    score = (significant_methods / 3) * max_abs
    if lag_detected:
        score = max(score, abs(ccf_peak))
    return Classification(rel_type, RECOMMENDED_METHODS[rel_type], round(min(score, 1.0), 3))

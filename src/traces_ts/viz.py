"""Visualization suite. Every function returns a matplotlib Figure."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib.colors import ListedColormap
from matplotlib.figure import Figure

from .classify import RELATIONSHIP_TYPES

if TYPE_CHECKING:
    from .analysis import AnalysisResult

TYPE_ABBREVIATIONS = {
    "linear": "LIN",
    "non_linear": "NL",
    "lagged": "LAG",
    "complex": "CX",
    "none": "",
}


def plot_correlation_comparison(
    result: AnalysisResult, top: int = 15, figsize: tuple[float, float] = (14, 6)
) -> Figure:
    """Grouped bars comparing Pearson, Spearman and Kendall for the strongest pairs."""
    data = result.table.nlargest(top, "max_abs_correlation").copy()
    data["pair"] = data["series_1"] + " / " + data["series_2"]
    melted = data.melt(
        id_vars="pair",
        value_vars=["pearson", "spearman", "kendall"],
        var_name="method",
        value_name="correlation",
    )
    fig, ax = plt.subplots(figsize=figsize)
    sns.barplot(data=melted, x="pair", y="correlation", hue="method", palette="Set2", ax=ax)
    ax.axhline(0, color="0.3", lw=0.8)
    ax.set_title(f"Correlation methods across the {len(data)} strongest pairs")
    ax.set_xlabel("")
    ax.tick_params(axis="x", rotation=45)
    plt.setp(ax.get_xticklabels(), ha="right")
    fig.tight_layout()
    return fig


def plot_relationship_matrix(
    result: AnalysisResult,
    value: str = "evidence_score",
    figsize: tuple[float, float] | None = None,
) -> Figure:
    """Lower-triangle matrix of all series, colored by ``value`` and labelled by relationship type.

    Grey cells were analysed but show no relationship; blank cells were not analysed
    (e.g. excluded parent/child pairs). ``LAG+k`` means the row series leads the column
    series by k observations.
    """
    names = result.data.series
    values = pd.DataFrame(np.nan, index=names, columns=names)
    labels = pd.DataFrame("", index=names, columns=names)
    unrelated = pd.DataFrame(False, index=names, columns=names)
    for row in result.table.itertuples(index=False):
        for a, b, sign in ((row.series_1, row.series_2, 1), (row.series_2, row.series_1, -1)):
            label = TYPE_ABBREVIATIONS[row.relationship_type]
            if row.relationship_type == "lagged":
                label += f"{sign * row.ccf_peak_lag:+d}"
            values.loc[a, b] = getattr(row, value)
            labels.loc[a, b] = label
            unrelated.loc[a, b] = row.relationship_type == "none"

    # Lower triangle without the empty first row and last column
    values, labels, unrelated = (df.iloc[1:, :-1] for df in (values, labels, unrelated))
    upper = np.triu(np.ones(values.shape, dtype=bool), k=1)
    size = len(names)
    figsize = figsize or (max(6, 0.8 * size + 3), max(5, 0.7 * size + 2))
    fig, ax = plt.subplots(figsize=figsize)
    common = {"linewidths": 0.5, "linecolor": "white", "square": True, "ax": ax}
    sns.heatmap(
        unrelated.astype(float),
        mask=upper | ~unrelated.to_numpy(),
        cmap=ListedColormap(["#e3e3e3"]),
        cbar=False,
        **common,
    )
    sns.heatmap(
        values,
        mask=upper | unrelated.to_numpy() | values.isna().to_numpy(),
        annot=labels,
        fmt="",
        cmap="viridis",
        vmin=0,
        vmax=1,
        cbar_kws={"label": value.replace("_", " ").capitalize()},
        **common,
    )
    ax.set_title(
        "Relationship matrix (LIN linear, NL non-linear, LAG lagged, CX complex; grey: none)"
    )
    fig.tight_layout()
    return fig


def plot_method_performance(
    result: AnalysisResult, figsize: tuple[float, float] = (10, 5)
) -> Figure:
    """Which correlation method was strongest, per relationship type."""
    counts = pd.crosstab(result.table["relationship_type"], result.table["strongest_method"])
    counts = counts.reindex([t for t in RELATIONSHIP_TYPES if t in counts.index])
    fig, ax = plt.subplots(figsize=figsize)
    counts.plot(kind="bar", stacked=True, ax=ax, color=sns.color_palette("Set2", counts.shape[1]))
    ax.set_title("Strongest correlation method by relationship type")
    ax.set_xlabel("Relationship type")
    ax.set_ylabel("Pairs")
    ax.tick_params(axis="x", rotation=0)
    ax.legend(title="Strongest method", bbox_to_anchor=(1.02, 1), loc="upper left")
    fig.tight_layout()
    return fig


def plot_ccf_overview(result: AnalysisResult, figsize: tuple[float, float] = (11, 6)) -> Figure:
    """Peak |CCF| versus the lag at which it occurs, for every pair."""
    t = result.table
    fig, ax = plt.subplots(figsize=figsize)
    detected = t["lag_detected"]
    sc = ax.scatter(
        t.loc[~detected, "ccf_peak_lag"],
        t.loc[~detected, "ccf_peak"].abs(),
        c=t.loc[~detected, "evidence_score"],
        cmap="viridis",
        vmin=0,
        vmax=1,
        s=60,
        alpha=0.6,
        label="no lead/lag detected",
    )
    ax.scatter(
        t.loc[detected, "ccf_peak_lag"],
        t.loc[detected, "ccf_peak"].abs(),
        c=t.loc[detected, "evidence_score"],
        cmap="viridis",
        vmin=0,
        vmax=1,
        s=140,
        marker="D",
        edgecolors="black",
        label="lead/lag detected",
    )
    for row in t[detected].itertuples(index=False):
        ax.annotate(
            f"{row.series_1}/{row.series_2}",
            (row.ccf_peak_lag, abs(row.ccf_peak)),
            xytext=(6, 4),
            textcoords="offset points",
            fontsize=8,
        )
    if len(t):
        ax.axhline(
            t["ccf_band"].median(), ls="--", color="firebrick", lw=1, label="significance band"
        )
    fig.colorbar(sc, ax=ax, label="Evidence score")
    kind = "pre-whitened " if result.config.prewhiten else ""
    ax.set_title(f"Peak {kind}cross-correlation vs lag (positive lag: series 1 leads)")
    ax.set_xlabel("Lag at peak |CCF|")
    ax.set_ylabel("|CCF| at peak")
    ax.margins(x=0.12)
    ax.grid(alpha=0.3)
    ax.legend(loc="best")
    fig.tight_layout()
    return fig


def plot_pair_ccf(
    result: AnalysisResult, series_1: str, series_2: str, figsize: tuple[float, float] = (10, 4.5)
) -> Figure:
    """CCF of one pair with significance band (and the raw CCF when pre-whitened)."""
    detail = result.pair(series_1, series_2)
    ccf = detail.ccf
    fig, ax = plt.subplots(figsize=figsize)
    ax.stem(ccf.lags, ccf.values, basefmt=" ", label="CCF used for detection")
    if result.config.prewhiten:
        ax.plot(
            detail.ccf_raw.lags,
            detail.ccf_raw.values,
            "o-",
            color="0.6",
            ms=3,
            lw=1,
            label="raw CCF (not pre-whitened)",
        )
    ax.axhspan(-ccf.band, ccf.band, color="firebrick", alpha=0.1, label="significance band")
    ax.axhline(0, color="0.3", lw=0.8)
    ax.set_xlabel(f"Lag k: corr({series_1}[t], {series_2}[t+k])")
    ax.set_ylabel("CCF")
    note = (
        f", pre-whitened AR({ccf.ar_order[0]})/AR({ccf.ar_order[1]})"
        if ccf.ar_order is not None
        else ""
    )
    ax.set_title(f"{series_1} vs {series_2}: peak {ccf.peak:+.2f} at lag {ccf.peak_lag:+d}{note}")
    ax.legend(loc="best", fontsize=8)
    fig.tight_layout()
    return fig


def plot_rolling_correlation(
    result: AnalysisResult, series_1: str, series_2: str, figsize: tuple[float, float] = (10, 4)
) -> Figure:
    """Rolling Pearson correlation of one pair over time."""
    detail = result.pair(series_1, series_2)
    fig, ax = plt.subplots(figsize=figsize)
    detail.rolling.plot(ax=ax, color="steelblue")
    ax.axhline(0, color="0.3", lw=0.8)
    ax.set_ylim(-1.05, 1.05)
    ax.set_title(
        f"{series_1} vs {series_2}: rolling correlation (window={result.config.rolling_window})"
    )
    ax.set_ylabel("Pearson r")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    return fig


def save_figures(
    result: AnalysisResult, out_dir: str | Path, *, top_pairs: int = 3, dpi: int = 150
) -> list[Path]:
    """Render the standard figures (plus per-pair CCF plots for the top pairs) to PNG files."""
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    figures: dict[str, Figure] = {
        "correlation_comparison": plot_correlation_comparison(result),
        "relationship_matrix": plot_relationship_matrix(result),
        "method_performance": plot_method_performance(result),
        "ccf_analysis": plot_ccf_overview(result),
    }
    if result.details:
        for row in result.top(top_pairs).itertuples(index=False):
            figures[f"ccf_{row.series_1}_{row.series_2}"] = plot_pair_ccf(
                result, row.series_1, row.series_2
            )
    paths = []
    for name, fig in figures.items():
        path = out / f"{name}.png"
        fig.savefig(path, dpi=dpi, bbox_inches="tight")
        plt.close(fig)
        paths.append(path)
    return paths

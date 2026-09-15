"""Regenerate docs/examples from the bundled sample datasets.

Usage:
    uv run python scripts/generate_examples.py
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import pandas as pd

from traces_ts import AnalysisConfig, analyze, load_data, render_markdown, viz

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "examples"
OUT = ROOT / "docs" / "examples"


def main() -> None:
    outputs = OUT / "outputs"
    outputs.mkdir(parents=True, exist_ok=True)

    data = load_data(DATA / "TRACES_sample_52x10_dataset_A1.xlsx")
    result = analyze(data)
    classic = analyze(data, AnalysisConfig.classic())

    result.to_csv(outputs / "results_A1.csv")
    (outputs / "report_A1.md").write_text(
        render_markdown(result, title="TRACES Example Report: dataset A1"), encoding="utf-8"
    )
    (outputs / "report_A1_classic.md").write_text(
        render_markdown(classic, title="TRACES Example Report: dataset A1 (classic, v1-style)"),
        encoding="utf-8",
    )

    comparison = pd.DataFrame(
        {
            "classic (v1-style)": classic.summary()["relationship_types"],
            "v2 default": result.summary()["relationship_types"],
        }
    )
    comparison.index.name = "relationship_type"
    comparison.to_csv(outputs / "classic_vs_v2_A1.csv")

    data_b = load_data(DATA / "TRACES_sample_52x10_dataset_B1.xlsx")
    (outputs / "report_B1.md").write_text(
        render_markdown(analyze(data_b), title="TRACES Example Report: dataset B1"),
        encoding="utf-8",
    )

    for path in viz.save_figures(result, OUT / "visualizations", top_pairs=2, dpi=110):
        print(path.relative_to(ROOT))
    for path in sorted(outputs.iterdir()):
        print(path.relative_to(ROOT))
    print(comparison)


if __name__ == "__main__":
    main()

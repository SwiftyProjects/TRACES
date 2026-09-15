import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd
import pytest
from matplotlib.figure import Figure

from traces_ts import __version__, analyze, load_data, render_markdown, viz
from traces_ts.cli import main

from .conftest import SAMPLE_A


@pytest.fixture(scope="module")
def result():
    return analyze(load_data(SAMPLE_A))


def test_summary(result):
    s = result.summary()
    assert s["n_pairs"] == 45
    assert sum(s["relationship_types"].values()) == 45
    assert sum(s["strength"].values()) == 45
    assert 0 <= s["significant_share"] <= 1
    assert isinstance(s["high_persistence_series"], list)


def test_markdown_report(result):
    md = render_markdown(result, top=5)
    assert md.startswith("# TRACES Analysis Report")
    assert "## Top 5 relationships" in md
    assert "| Label_3 | Label_10 | linear |" in md


@pytest.mark.parametrize(
    "func",
    [
        "plot_correlation_comparison",
        "plot_relationship_matrix",
        "plot_method_performance",
        "plot_ccf_overview",
    ],
)
def test_overview_plots(result, func):
    fig = getattr(viz, func)(result)
    assert isinstance(fig, Figure)
    plt.close(fig)


def test_pair_plots(result):
    for func in (viz.plot_pair_ccf, viz.plot_rolling_correlation):
        fig = func(result, "Label_3", "Label_10")
        assert isinstance(fig, Figure)
        plt.close(fig)


def test_method_performance_legend_is_clean(result):
    fig = viz.plot_method_performance(result)
    labels = [t.get_text() for t in fig.axes[0].get_legend().get_texts()]
    assert labels
    assert all("count" not in label and "(" not in label for label in labels)
    plt.close(fig)


def test_save_figures(result, tmp_path):
    paths = viz.save_figures(result, tmp_path, top_pairs=2, dpi=50)
    assert len(paths) == 6
    assert all(p.exists() for p in paths)


def test_cli_analyze(sample_path, tmp_path, capsys):
    out = tmp_path / "results"
    code = main(
        [
            "analyze",
            str(sample_path),
            "-o",
            str(out),
            "--max-lag",
            "8",
            "--exclude",
            "Label_1=Label_2,Label_3",
            "--no-figures",
        ]
    )
    assert code == 0
    assert len(pd.read_csv(out / "results.csv")) == 43
    assert (out / "results.xlsx").exists()
    assert (out / "report.md").exists()
    assert "Analysed 43 pairs" in capsys.readouterr().out


def test_cli_classic_and_errors(sample_path, tmp_path, capsys):
    args = [
        "analyze",
        str(sample_path),
        "-o",
        str(tmp_path),
        "--classic",
        "--no-excel",
        "--no-figures",
    ]
    assert main(args) == 0
    assert main(["analyze", str(tmp_path / "missing.xlsx")]) == 2
    assert "error:" in capsys.readouterr().err


def test_cli_bad_exclude(sample_path, tmp_path, capsys):
    assert main(["analyze", str(sample_path), "-o", str(tmp_path), "--exclude", "bad"]) == 2
    assert "PARENT=CHILD" in capsys.readouterr().err


def test_cli_version(capsys):
    with pytest.raises(SystemExit):
        main(["--version"])
    assert __version__ in capsys.readouterr().out

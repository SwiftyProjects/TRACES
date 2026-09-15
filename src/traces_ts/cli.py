"""Command-line interface: ``traces analyze data.xlsx``."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from . import __version__
from .config import DETREND_OPTIONS, AnalysisConfig
from .io import MISSING_OPTIONS


def _parse_exclude(values: Sequence[str]) -> dict[str, list[str]]:
    mapping: dict[str, list[str]] = {}
    for value in values:
        parent, sep, children = value.partition("=")
        if not sep or not parent or not children:
            raise ValueError(f"--exclude expects PARENT=CHILD[,CHILD...], got {value!r}")
        mapping.setdefault(parent.strip(), []).extend(
            c.strip() for c in children.split(",") if c.strip()
        )
    return mapping


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="traces",
        description="TRACES: Time-series Relationship Analysis with Comprehensive Evaluation Suite",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    a = sub.add_parser("analyze", help="Analyse all series pairs in an Excel or CSV file")
    a.add_argument("path", type=Path, help="Input .xlsx/.xls/.csv file")
    a.add_argument(
        "-o",
        "--out",
        type=Path,
        default=Path("results"),
        help="Output directory (default: results)",
    )
    a.add_argument("--time-column", help="Time column name (default: first column)")
    a.add_argument("--sheet", default=0, help="Excel worksheet name or index (default: first)")
    a.add_argument(
        "--missing", choices=MISSING_OPTIONS, default="raise", help="Missing value policy"
    )
    a.add_argument(
        "--exclude",
        action="append",
        default=[],
        metavar="PARENT=CHILD[,CHILD]",
        help="Exclude parent/child pairs (repeatable)",
    )

    defaults = AnalysisConfig()
    a.add_argument("--rolling-window", type=int, default=defaults.rolling_window)
    a.add_argument("--max-lag", type=int, default=defaults.max_lag)
    a.add_argument("--alpha", type=float, default=defaults.alpha)
    a.add_argument("--min-correlation", type=float, default=defaults.min_correlation)
    a.add_argument("--detrend", choices=DETREND_OPTIONS, default=defaults.detrend)
    a.add_argument(
        "--no-autocorrelation-adjustment",
        action="store_true",
        help="Use naive p-values that assume independent observations",
    )
    a.add_argument(
        "--no-fdr", action="store_true", help="Disable Benjamini-Hochberg FDR correction"
    )
    a.add_argument("--no-prewhiten", action="store_true", help="Detect lags on the raw CCF")
    a.add_argument(
        "--classic",
        action="store_true",
        help="Shortcut for all three --no-* safeguards (closest to TRACES v1)",
    )
    a.add_argument("--top", type=int, default=10, help="Pairs to list in the report (default: 10)")
    a.add_argument("--no-figures", action="store_true", help="Skip PNG figure export")
    a.add_argument("--no-excel", action="store_true", help="Skip results.xlsx export")
    return parser


def run_analyze(args: argparse.Namespace) -> int:
    from .analysis import analyze
    from .io import load_data
    from .report import render_markdown

    sheet = int(args.sheet) if str(args.sheet).isdigit() else args.sheet
    data = load_data(
        args.path, time_column=args.time_column, sheet_name=sheet, missing=args.missing
    )
    config = AnalysisConfig(
        rolling_window=args.rolling_window,
        max_lag=args.max_lag,
        alpha=args.alpha,
        min_correlation=args.min_correlation,
        detrend=args.detrend,
        autocorrelation_adjustment=not (args.no_autocorrelation_adjustment or args.classic),
        fdr_correction=not (args.no_fdr or args.classic),
        prewhiten=not (args.no_prewhiten or args.classic),
    )
    result = analyze(data, config, exclude=_parse_exclude(args.exclude) or None)

    out: Path = args.out
    out.mkdir(parents=True, exist_ok=True)
    written = [result.to_csv(out / "results.csv")]
    if not args.no_excel:
        written.append(result.to_excel(out / "results.xlsx"))
    report = out / "report.md"
    report.write_text(render_markdown(result, top=args.top), encoding="utf-8")
    written.append(report)
    if not args.no_figures:
        import matplotlib

        matplotlib.use("Agg")
        from .viz import save_figures

        written.extend(save_figures(result, out / "figures"))

    counts = ", ".join(f"{k}={v}" for k, v in result.summary()["relationship_types"].items() if v)
    print(f"Analysed {len(result.table)} pairs from {data.source}: {counts}")
    for path in written:
        print(f"  wrote {path}")
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "analyze":
            return run_analyze(args)
    except (FileNotFoundError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    parser.error(f"unknown command {args.command!r}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())

"""CLI for rendering a Lean proof-attempt diagnostics report."""

from __future__ import annotations

import argparse
from pathlib import Path

from .analyzer import analyze, load_attempts, render_markdown


def main() -> int:
    parser = argparse.ArgumentParser(description="Analyze Lean proof-attempt JSONL artifacts.")
    parser.add_argument("input", help="path to JSONL attempt records")
    parser.add_argument("--output", type=Path, help="write Markdown report to this path")
    parser.add_argument("--title", default="Lean proof diagnostics report")
    args = parser.parse_args()
    report = render_markdown(analyze(load_attempts(args.input)), args.title)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(report, encoding="utf-8")
    else:
        print(report, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

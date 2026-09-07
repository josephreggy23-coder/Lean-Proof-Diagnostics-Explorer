"""CLI for rendering a Lean proof-attempt diagnostics report."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .analyzer import analyze, load_attempts, render_markdown


def main() -> int:
    parser = argparse.ArgumentParser(description="Analyze Lean proof-attempt JSONL artifacts.")
    parser.add_argument("input", help="path to JSONL attempt records")
    parser.add_argument("--output", type=Path, help="write the selected report format to this path")
    parser.add_argument("--title", default="Lean proof diagnostics report")
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    args = parser.parse_args()
    summary = analyze(load_attempts(args.input))
    report = (
        json.dumps(summary, indent=2, sort_keys=True) + "\n"
        if args.format == "json"
        else render_markdown(summary, args.title)
    )
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(report, encoding="utf-8")
    else:
        print(report, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

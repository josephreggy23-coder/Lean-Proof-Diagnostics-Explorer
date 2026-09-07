"""Rule-based categorization and example-level summaries of Lean attempt logs."""

from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable
import json


RULES: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("placeholder_proof", ("sorry", "admit")),
    ("timeout", ("timed out", "maximum heartbeats", "maximum recursion depth")),
    ("unknown_tactic", ("unknown tactic",)),
    ("tactic_failure", ("tactic `", "tactic failed")),
    ("unknown_identifier", ("unknown identifier", "unknown constant")),
    ("type_mismatch", ("type mismatch", "application type mismatch")),
    ("unsolved_goals", ("unsolved goals", "goals accomplished")),
    ("parser_error", ("unexpected token", "failed to parse", "invalid syntax")),
)


def classify_diagnostic(diagnostics: str) -> str:
    """Return the first matching transparent error category, or ``other``."""
    lowered = diagnostics.lower()
    for label, signals in RULES:
        if any(signal in lowered for signal in signals):
            return label
    return "other"


def load_attempts(path: str | Path) -> list[dict[str, Any]]:
    """Load JSONL and reject records that cannot identify an example or result."""
    attempts: list[dict[str, Any]] = []
    for line_number, line in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        record = json.loads(line)
        missing = {"item_id", "accepted"} - record.keys()
        if missing:
            raise ValueError(f"line {line_number}: missing {sorted(missing)}")
        if not isinstance(record["accepted"], bool):
            raise ValueError(f"line {line_number}: accepted must be boolean")
        attempts.append(record)
    return attempts


def analyze(attempts: Iterable[dict[str, Any]]) -> dict[str, Any]:
    """Aggregate raw attempt records without collapsing repair outcomes."""
    by_item: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for attempt in attempts:
        by_item[str(attempt["item_id"])].append(attempt)
    for records in by_item.values():
        records.sort(key=lambda row: int(row.get("round", 0)))

    failure_counts: Counter[str] = Counter()
    phase_counts: Counter[str] = Counter()
    first_pass = repaired = eventual = 0
    total_seconds = 0.0
    attempts_count = 0
    for records in by_item.values():
        attempts_count += len(records)
        phase_counts.update(str(row.get("phase", "unspecified")) for row in records)
        total_seconds += sum(float(row.get("elapsed_seconds", 0.0)) for row in records)
        accepted = any(row["accepted"] for row in records)
        first_accepted = records[0]["accepted"]
        eventual += int(accepted)
        first_pass += int(first_accepted)
        repaired += int(accepted and not first_accepted)
        for row in records:
            if not row["accepted"]:
                failure_counts[classify_diagnostic(str(row.get("diagnostics", "")))] += 1

    examples = len(by_item)
    return {
        "examples": examples,
        "attempts": attempts_count,
        "first_pass_successes": first_pass,
        "eventual_successes": eventual,
        "repaired_successes": repaired,
        "first_pass_rate": first_pass / examples if examples else 0.0,
        "eventual_success_rate": eventual / examples if examples else 0.0,
        "mean_attempts_per_example": attempts_count / examples if examples else 0.0,
        "verification_seconds": total_seconds,
        "phase_counts": dict(sorted(phase_counts.items())),
        "failure_categories": dict(sorted(failure_counts.items())),
    }


def render_markdown(summary: dict[str, Any], title: str = "Lean proof diagnostics report") -> str:
    """Render a dependency-free report suitable for committing beside an experiment."""
    percent = lambda value: f"{value * 100:.1f}%"
    lines = [
        f"# {title}", "", "## Outcome summary", "",
        "| Metric | Value |", "| --- | ---: |",
        f"| Examples | {summary['examples']} |",
        f"| Attempts | {summary['attempts']} |",
        f"| First-pass successes | {summary['first_pass_successes']} ({percent(summary['first_pass_rate'])}) |",
        f"| Eventual successes | {summary['eventual_successes']} ({percent(summary['eventual_success_rate'])}) |",
        f"| Repair-only successes | {summary['repaired_successes']} |",
        f"| Mean attempts/example | {summary['mean_attempts_per_example']:.2f} |",
        f"| Lean checking time | {summary['verification_seconds']:.3f} s |",
        "", "## Rejected-attempt categories", "",
        "| Category | Count |", "| --- | ---: |",
    ]
    categories = summary["failure_categories"]
    if categories:
        lines.extend(f"| `{label}` | {count} |" for label, count in categories.items())
    else:
        lines.append("| _No rejected attempts_ | 0 |")
    lines.extend(["", "## Attempt phases", "", "| Phase | Attempts |", "| --- | ---: |"])
    phases = summary["phase_counts"]
    if phases:
        lines.extend(f"| `{phase}` | {count} |" for phase, count in phases.items())
    else:
        lines.append("| _No attempts_ | 0 |")
    return "\n".join(lines) + "\n"

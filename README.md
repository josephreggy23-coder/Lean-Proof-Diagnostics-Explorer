# Lean Proof Diagnostics Explorer

> Turn Lean compiler feedback into a compact, reproducible failure analysis.

Language-model proof experiments often report a single success rate and discard
the rejected proofs. This small tool keeps the failed artifacts useful: it reads
attempt-level JSONL logs, classifies common Lean failures, and emits an auditable
Markdown report.

## What it answers

- How many examples passed on the first try versus after repair?
- Which Lean failure modes were most common?
- Did iterative repair yield additional verified proofs?
- Which examples passed immediately, were repaired, or remain unresolved?
- How many verifier calls and how much checking time did an experiment require?
- Which attempt phases (formalization, repair, or manual baseline) produced the artifacts?

## Input contract

One JSON object per attempt, with the fields produced by the companion
autoformalization project:

```json
{"item_id":"zero_mul","phase":"repair","round":1,"accepted":false,"diagnostics":"unknown tactic","elapsed_seconds":0.18}
```

Only `item_id` and `accepted` are required. Missing optional fields are handled
gracefully, so old experiment logs remain usable.

## Failure taxonomy

| Category | Typical Lean signal |
| --- | --- |
| `unknown_identifier` | unknown identifier / unknown constant |
| `unknown_tactic` | unknown tactic |
| `tactic_failure` | a recognized tactic failed to close the goal |
| `type_mismatch` | type mismatch / application type mismatch |
| `unsolved_goals` | unsolved goals / goals accomplished? |
| `parser_error` | unexpected token / failed to parse |
| `timeout` | timed out / maximum heartbeats |
| `placeholder_proof` | `sorry` / `admit` |
| `other` | Any unmatched diagnostic |

The classifier is deliberately rule-based and transparent—not an LLM labeler.
You can inspect, extend, or version every mapping in `analyzer.py`.

## Quick start

```powershell
git clone https://github.com/josephreggy23-coder/Lean-Proof-Diagnostics-Explorer.git
cd Lean-Proof-Diagnostics-Explorer
python -m pip install -e .
python -m proof_diagnostics examples/real_run.jsonl
```

Write the report to a file:

```powershell
python -m proof_diagnostics examples/real_run.jsonl --output artifacts/report.md
```

To inspect both the accepted theorem and a real, controlled Lean rejection:

```powershell
python -m proof_diagnostics examples/real_controlled_attempts.jsonl
```

Request the same summary as machine-readable JSON for plotting or a notebook:

```powershell
python -m proof_diagnostics examples/real_controlled_attempts.jsonl --format json
```

Run tests:

```powershell
python -m unittest discover -s tests -v
```

## Example output

The included real baseline is a Lean-Web-checked theorem:
`example (n : ℕ) : n + 0 = n := by omega`. It has one accepted attempt and is
explicitly marked `manual_baseline`, because no language model generated it.
See [`examples/REAL_EXAMPLE.md`](examples/REAL_EXAMPLE.md) for its exact source,
verification environment, and provenance. Bring your own LLM experiment JSONL
to obtain repair statistics; this project never fabricates them.

## Design principles

- **Example-level reporting:** one theorem is not allowed to inflate results by
  generating many attempts.
- **Failures are retained:** unmatched errors become `other`, never disappear.
- **No hidden model dependency:** Python standard library only.
- **Reproducible summaries:** the same JSONL input always produces the same
  report.

## Relationship to the companion project

This repository consumes the JSONL attempt artifacts from
[Autoformalization and Iterative Proof Repair with Lean and Language Models](https://github.com/josephreggy23-coder/Autoformalization-and-Iterative-Proof-Repair-with-Lean-and-Language-Models).
Together, the projects provide a generation/verification loop and a transparent
post-hoc analysis layer.

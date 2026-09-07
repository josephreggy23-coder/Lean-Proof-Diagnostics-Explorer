# Real Lean verification example

This directory contains a real Lean 4 theorem, not a fabricated attempt log.
The source in [`nat_add_zero.lean`](nat_add_zero.lean) was checked on
2026-09-07 in [Lean Web](https://live.lean-lang.org/), using **Latest Mathlib
with Lean v4.34.0-rc2**. Lean reported **No goals** and **0 messages**.

```lean
import Mathlib

example (n : ℕ) : n + 0 = n := by
  omega
```

`real_run.jsonl` preserves that single successful verification as a
`manual_baseline` record. It is intentionally not described as an LLM result:
no language model generated this source, and no timing was recorded by the web
editor. The record demonstrates the exact input format expected by the
diagnostics tool without inventing model behavior or error messages.

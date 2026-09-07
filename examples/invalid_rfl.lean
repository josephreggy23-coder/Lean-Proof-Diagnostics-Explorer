import Mathlib

/-- Intentionally invalid: captured to document a genuine Lean diagnostic. -/
example (n : ℕ) : n + 1 = n := by
  rfl

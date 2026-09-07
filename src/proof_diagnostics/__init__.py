"""Transparent Lean proof-attempt diagnostics and experiment summaries."""

from .analyzer import analyze, classify_diagnostic, render_markdown

__all__ = ["analyze", "classify_diagnostic", "render_markdown"]

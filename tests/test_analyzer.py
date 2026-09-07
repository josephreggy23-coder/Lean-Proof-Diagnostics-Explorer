import unittest

from proof_diagnostics.analyzer import analyze, classify_diagnostic, render_markdown


class AnalyzerTests(unittest.TestCase):
    def test_classifier_covers_known_and_unknown_diagnostics(self):
        self.assertEqual(classify_diagnostic("error: unknown tactic 'foo'"), "unknown_tactic")
        self.assertEqual(classify_diagnostic("something novel"), "other")

    def test_summary_is_example_level_and_counts_repair_gain(self):
        summary = analyze([
            {"item_id": "a", "accepted": True, "round": 0, "elapsed_seconds": 0.1},
            {"item_id": "b", "accepted": False, "round": 0, "diagnostics": "type mismatch"},
            {"item_id": "b", "accepted": True, "round": 1},
        ])
        self.assertEqual(summary["examples"], 2)
        self.assertEqual(summary["attempts"], 3)
        self.assertEqual(summary["first_pass_successes"], 1)
        self.assertEqual(summary["repaired_successes"], 1)
        self.assertEqual(summary["failure_categories"], {"type_mismatch": 1})

    def test_report_includes_category_table(self):
        report = render_markdown(analyze([]))
        self.assertIn("No rejected attempts", report)

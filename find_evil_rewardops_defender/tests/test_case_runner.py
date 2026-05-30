from __future__ import annotations

import json
import unittest

from dfir_triage_agent import case_runner


class CaseRunnerTests(unittest.TestCase):
    def test_default_case_passes_ground_truth(self) -> None:
        case = case_runner.load_case(case_runner.DEFAULT_CASE)
        report = case_runner.build_case_report(case)

        self.assertTrue(report["score"]["passes_ground_truth"])
        self.assertEqual(report["score"]["event_precision"], 1.0)
        self.assertEqual(report["score"]["event_recall"], 1.0)
        self.assertEqual(report["score"]["false_positive_events"], [])
        self.assertEqual(report["score"]["false_negative_events"], [])
        self.assertIn("agent_tool_abuse", report["defender_verdict"])

    def test_score_reports_signal_misses(self) -> None:
        case = case_runner.load_case(case_runner.DEFAULT_CASE)
        case = json.loads(json.dumps(case))
        case["ground_truth"]["event_labels"]["evt-004"]["expected_signals"].append("not_a_real_signal")

        report = case_runner.build_case_report(case)

        self.assertFalse(report["score"]["passes_ground_truth"])
        self.assertEqual(report["score"]["signal_misses"][0]["case_event_id"], "evt-004")


if __name__ == "__main__":
    unittest.main()

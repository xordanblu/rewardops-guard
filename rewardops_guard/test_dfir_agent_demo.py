from __future__ import annotations

import unittest

from rewardops_guard import dfir_agent_demo


class DfirAgentDemoTest(unittest.TestCase):
    def test_default_demo_finds_credential_exfil_and_tool_injection(self) -> None:
        report = dfir_agent_demo.build_report(dfir_agent_demo.DEFAULT_EVENTS)

        self.assertIn("credential_theft", report["verdict"])
        self.assertIn("agent_prompt_injection", report["verdict"])
        self.assertGreaterEqual(report["high_event_count"], 2)
        self.assertIn("credential_access", report["signal_counts"])
        self.assertIn("unsafe_tool_request", report["signal_counts"])

    def test_report_does_not_store_raw_detail_text(self) -> None:
        marker_value = "PRIVATE-RAW-LOG-DO-NOT-STORE"
        report = dfir_agent_demo.build_report(
            [
                {
                    "ts": "2026-05-28T00:00:00Z",
                    "host": "h1",
                    "source": "endpoint",
                    "event_type": "process",
                    "actor": "user",
                    "detail": f"powershell -enc {marker_value}",
                }
            ]
        )

        rendered = str(report)
        self.assertNotIn(marker_value, rendered)
        self.assertIn("detail_sha256", report["timeline"][0])
        self.assertNotIn("detail", report["timeline"][0])

    def test_clean_events_remain_low_risk(self) -> None:
        report = dfir_agent_demo.build_report(
            [
                {
                    "ts": "2026-05-28T00:00:00Z",
                    "host": "h1",
                    "source": "policy",
                    "event_type": "decision",
                    "actor": "guard",
                    "detail": "allowed local report generation after preflight",
                }
            ]
        )

        self.assertEqual(report["high_event_count"], 0)
        self.assertEqual(report["timeline"][0]["severity"], "info")


if __name__ == "__main__":
    unittest.main()

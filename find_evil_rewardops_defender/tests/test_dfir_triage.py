from __future__ import annotations

import unittest

from dfir_triage_agent.dfir_triage import build_report, redact, score_event


class DfirTriageTests(unittest.TestCase):
    def test_redacts_email_and_token_like_values(self) -> None:
        redacted = redact({"user": "analyst@example.com", "token": "a" * 32})
        self.assertEqual(redacted["user"], "[redacted-email]")
        self.assertEqual(redacted["token"], "[redacted-token]")

    def test_scores_encoded_powershell(self) -> None:
        scored = score_event({"event_type": "process_start", "command_line": "powershell -EncodedCommand SQBFAFgA"})
        rules = {finding["rule"] for finding in scored["findings"]}
        self.assertIn("encodedcommand", rules)
        self.assertGreaterEqual(scored["score"], 40)

    def test_builds_validated_accuracy_report(self) -> None:
        report = build_report(
            [
                {
                    "ts": "2026-05-29T01:00:00Z",
                    "host": "h1",
                    "event_type": "process_start",
                    "command_line": "mimikatz",
                    "expected_rules": ["mimikatz"],
                },
                {
                    "ts": "2026-05-29T01:01:00Z",
                    "host": "h1",
                    "event_type": "network_connection",
                    "dst": "8.8.8.8",
                    "expected_rules": ["external_connection"],
                },
            ],
            case_id="case-1",
        )
        self.assertEqual(report["case_id"], "case-1")
        self.assertIn(report["severity"], {"high", "critical"})
        self.assertEqual(report["event_count"], 2)
        self.assertGreaterEqual(report["finding_count"], 2)
        self.assertEqual(report["accuracy_report"]["status"], "validated")
        self.assertEqual(report["accuracy_report"]["recall"], 1.0)
        self.assertIn("audit_trail", report)

    def test_self_corrects_private_network_as_non_external(self) -> None:
        scored = score_event({"event_type": "network_connection", "dst": "172.20.0.4"})

        rules = {finding["rule"] for finding in scored["findings"]}
        self.assertNotIn("external_connection", rules)
        self.assertEqual(scored["score"], 0)
        self.assertEqual(scored["corrections"][0]["rule"], "external_connection")


if __name__ == "__main__":
    unittest.main()

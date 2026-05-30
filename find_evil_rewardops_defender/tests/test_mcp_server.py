from __future__ import annotations

import json
import tempfile
from pathlib import Path
import unittest

from dfir_triage_agent.mcp_server import handle_request


ROOT = Path(__file__).resolve().parents[1]
SAMPLE = ROOT / "dfir_triage_agent" / "sample_events.jsonl"


class DfirMcpServerTests(unittest.TestCase):
    def call(self, name: str, arguments: dict[str, object]) -> dict[str, object]:
        response = handle_request(
            {
                "jsonrpc": "2.0",
                "id": "test",
                "method": "tools/call",
                "params": {"name": name, "arguments": arguments},
            }
        )
        self.assertNotIn("error", response)
        return response["result"]  # type: ignore[return-value]

    def test_lists_tools(self) -> None:
        response = handle_request({"jsonrpc": "2.0", "id": 1, "method": "tools/list"})
        self.assertIn("triage_case", response["result"]["tools"])
        self.assertIn("export_report", response["result"]["tools"])

    def test_triage_case_returns_compact_report(self) -> None:
        result = self.call("triage_case", {"path": str(SAMPLE), "case_id": "unit"})
        self.assertEqual(result["severity"], "critical")
        self.assertEqual(result["event_count"], 5)
        self.assertGreaterEqual(result["finding_count"], 5)
        self.assertIn("timeline", result)

    def test_explain_evidence_redacts_sensitive_values(self) -> None:
        api_token = "sk-" + "secret-token-1234567890"
        result = self.call(
            "explain_evidence",
            {
                "event": {
                    "event_type": "process",
                    "host": "laptop",
                    "command": f"powershell -EncodedCommand {api_token} user@example.com",
                }
            },
        )
        redacted = json.dumps(result["redacted_event"])
        self.assertNotIn("user@example.com", redacted)
        self.assertNotIn(api_token, redacted)
        self.assertGreater(result["score"], 0)

    def test_export_report_writes_json_and_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            json_output = Path(tmp) / "report.json"
            markdown_output = Path(tmp) / "report.md"
            result = self.call(
                "export_report",
                {
                    "path": str(SAMPLE),
                    "case_id": "export-unit",
                    "json_output": str(json_output),
                    "markdown_output": str(markdown_output),
                },
            )
            self.assertEqual(result["severity"], "critical")
            self.assertTrue(json_output.exists())
            self.assertTrue(markdown_output.exists())

    def test_unknown_tool_is_error(self) -> None:
        response = handle_request(
            {
                "jsonrpc": "2.0",
                "id": "bad",
                "method": "tools/call",
                "params": {"name": "delete_host", "arguments": {}},
            }
        )
        self.assertIn("error", response)


if __name__ == "__main__":
    unittest.main()

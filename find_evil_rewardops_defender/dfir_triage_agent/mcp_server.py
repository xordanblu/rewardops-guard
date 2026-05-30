#!/usr/bin/env python3
"""Read-only JSON-RPC wrapper for the DFIR triage kit.

The interface is intentionally small and deterministic so it can be adapted to
an MCP server or embedded in an incident-response agent loop without granting
live host access.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

from .dfir_triage import build_report, load_events, score_event, write_markdown


TOOLS = {
    "load_case_events": {
        "description": "Load sanitized JSONL/JSON case events and return count plus redacted event hashes.",
        "required": ["path"],
    },
    "triage_case": {
        "description": "Build a severity-ranked DFIR triage report from sanitized local events.",
        "required": ["path"],
    },
    "explain_evidence": {
        "description": "Explain rule hits for one sanitized event object.",
        "required": ["event"],
    },
    "export_report": {
        "description": "Write JSON and Markdown triage reports for a local sanitized event file.",
        "required": ["path", "json_output", "markdown_output"],
    },
}


def safe_path(value: Any) -> Path:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("path must be a non-empty string")
    path = Path(value).expanduser()
    if not path.exists():
        raise FileNotFoundError(str(path))
    if not path.is_file():
        raise ValueError("path must point to a file")
    return path


def handle_tool(name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    if name == "list_tools":
        return {"tools": TOOLS}
    if name not in TOOLS:
        raise ValueError(f"unknown tool: {name}")
    if not isinstance(arguments, dict):
        raise ValueError("arguments must be an object")

    if name == "load_case_events":
        events = load_events(safe_path(arguments.get("path")))
        scored = [score_event(event) for event in events]
        return {
            "event_count": len(events),
            "event_hashes": [item["event_hash"] for item in scored],
            "safe_boundaries": [
                "local sanitized files only",
                "no live probing",
                "tokens and emails are redacted before hashing",
            ],
        }

    if name == "triage_case":
        events = load_events(safe_path(arguments.get("path")))
        case_id = str(arguments.get("case_id") or "mcp-case")
        report = build_report(events, case_id=case_id)
        return {
            "case_id": report["case_id"],
            "severity": report["severity"],
            "event_count": report["event_count"],
            "finding_count": report["finding_count"],
            "max_event_score": report["max_event_score"],
            "containment_checklist": report["containment_checklist"],
            "timeline": [
                {
                    "ts": item["ts"],
                    "host": item["host"],
                    "event_type": item["event_type"],
                    "score": item["score"],
                    "event_hash": item["event_hash"],
                    "findings": [finding["title"] for finding in item["findings"]],
                }
                for item in report["timeline"]
            ],
        }

    if name == "explain_evidence":
        event = arguments.get("event")
        if not isinstance(event, dict):
            raise ValueError("event must be an object")
        scored = score_event(event)
        return {
            "event_hash": scored["event_hash"],
            "score": scored["score"],
            "findings": scored["findings"],
            "redacted_event": scored["redacted_event"],
        }

    if name == "export_report":
        events = load_events(safe_path(arguments.get("path")))
        report = build_report(events, case_id=str(arguments.get("case_id") or "mcp-case"))
        json_output = Path(str(arguments.get("json_output") or "")).expanduser()
        markdown_output = Path(str(arguments.get("markdown_output") or "")).expanduser()
        if not str(json_output) or not str(markdown_output):
            raise ValueError("json_output and markdown_output are required")
        json_output.parent.mkdir(parents=True, exist_ok=True)
        json_output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        write_markdown(markdown_output, report)
        return {
            "severity": report["severity"],
            "event_count": report["event_count"],
            "finding_count": report["finding_count"],
            "json_output": str(json_output),
            "markdown_output": str(markdown_output),
        }

    raise AssertionError("unreachable")


def handle_request(request: dict[str, Any]) -> dict[str, Any]:
    request_id = request.get("id")
    try:
        method = request.get("method")
        params = request.get("params") or {}
        if method == "tools/list":
            result = handle_tool("list_tools", {})
        elif method == "tools/call":
            result = handle_tool(str(params.get("name") or ""), params.get("arguments") or {})
        else:
            raise ValueError(f"unknown method: {method}")
        return {"jsonrpc": "2.0", "id": request_id, "result": result}
    except Exception as exc:
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32000, "message": f"{type(exc).__name__}: {exc}"},
        }


def serve() -> int:
    for line in sys.stdin:
        if not line.strip():
            continue
        try:
            request = json.loads(line)
            if not isinstance(request, dict):
                raise ValueError("request must be an object")
            response = handle_request(request)
        except Exception as exc:
            response = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32700, "message": f"{type(exc).__name__}: {exc}"},
            }
        print(json.dumps(response, sort_keys=True), flush=True)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the read-only DFIR JSON-RPC wrapper.")
    parser.add_argument("--oneshot", help="JSON request to handle and print once")
    args = parser.parse_args()
    if args.oneshot:
        response = handle_request(json.loads(args.oneshot))
        print(json.dumps(response, indent=2, sort_keys=True))
        return 0
    return serve()


if __name__ == "__main__":
    raise SystemExit(main())

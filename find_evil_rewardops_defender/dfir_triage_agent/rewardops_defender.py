#!/usr/bin/env python3
"""Sequence-aware agent-defense demo for FIND EVIL.

This module complements the DFIR triage rules with an agent-security timeline:
prompt-injection attempts, wallet-signing traps, endpoint activity, and network
egress are scored together. Raw event details are hashed rather than retained.
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
import unicodedata


BENIGN_CONTEXT_SOURCES = {"training_doc", "documentation", "security_blog"}
LEET_TRANSLATION = str.maketrans({"0": "o", "1": "i", "3": "e", "4": "a", "5": "s", "7": "t", "@": "a", "$": "s"})
FOLDED_SIGNAL_TARGETS = [
    "system prompt",
    "developer instructions",
    "internal instructions",
    "hidden instructions",
    "tool schema",
    "ignore previous instructions",
]

SIGNALS: list[tuple[str, int, str, str]] = [
    (
        "agent_prompt_injection",
        5,
        r"\b(ignore|developer instructions|system prompt|hidden instructions|paste internal)\b",
        "hostile instruction aimed at agent control or prompt disclosure",
    ),
    (
        "wallet_trap",
        5,
        r"\b(connect wallet|sign transaction|sign message|approve transaction|release reward)\b",
        "payment-capable approval request",
    ),
    (
        "encoded_execution",
        3,
        r"\b(-enc|encodedcommand|frombase64string|powershell)\b",
        "encoded or script execution",
    ),
    (
        "credential_access",
        5,
        r"\b(reg save|sam\.save|lsass|mimikatz|\.ssh|shadow|keychain)\b",
        "credential material access pattern",
    ),
    (
        "exfiltration",
        5,
        r"\b(curl|wget|http[s]?://|upload|scp|rclone|file=@)\b",
        "outbound transfer or upload pattern",
    ),
]


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def one_line(value: Any, limit: int = 140) -> str:
    return " ".join(str(value or "").split())[:limit]


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8", errors="replace")).hexdigest()


def fold_obfuscation(value: str) -> str:
    normalized = unicodedata.normalize("NFKC", value).translate(LEET_TRANSLATION).lower()
    decomposed = unicodedata.normalize("NFKD", normalized)
    without_marks = "".join(ch for ch in decomposed if not unicodedata.combining(ch))
    return re.sub(r"[^a-z0-9]+", "", without_marks)


def load_events(path: Path) -> list[dict[str, Any]]:
    text = path.read_text(encoding="utf-8")
    stripped = text.strip()
    if not stripped:
        return []
    if stripped.startswith("["):
        payload = json.loads(stripped)
        if not isinstance(payload, list):
            raise ValueError("JSON input must be an array")
        return [item for item in payload if isinstance(item, dict)]
    events = []
    for lineno, line in enumerate(text.splitlines(), start=1):
        if not line.strip():
            continue
        item = json.loads(line)
        if not isinstance(item, dict):
            raise ValueError(f"line {lineno} is not an object")
        events.append(item)
    return events


def classify(detail: str) -> tuple[list[str], int, list[str]]:
    signals: list[str] = []
    score = 0
    explanations: list[str] = []
    for signal_id, weight, pattern, explanation in SIGNALS:
        if re.search(pattern, detail, flags=re.IGNORECASE):
            signals.append(signal_id)
            score += weight
            explanations.append(explanation)
    folded = fold_obfuscation(detail)
    if any(fold_obfuscation(target) in folded for target in FOLDED_SIGNAL_TARGETS):
        signals.append("obfuscated_prompt_smuggling")
        score += 5
        explanations.append("spaced or leetspeak prompt-injection/exfiltration phrase")
    return signals, score, explanations


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
    source = one_line(raw.get("source"), 40)
    signals, score, explanations = classify(detail)
    benign_adjustment = source in BENIGN_CONTEXT_SOURCES and bool(signals)
    adjusted_score = min(score, 1) if benign_adjustment else score
    detail_hash = sha256_text(detail)
    event_id = sha256_text(
        "|".join(
            [
                str(raw.get("ts") or raw.get("timestamp") or ""),
                str(raw.get("host") or ""),
                source,
                str(raw.get("event_type") or ""),
                detail_hash,
            ]
        )
    )[:16]
    return {
        "event_id": event_id,
        "ts": one_line(raw.get("ts") or raw.get("timestamp"), 40),
        "host": one_line(raw.get("host"), 80),
        "source": source,
        "event_type": one_line(raw.get("event_type"), 40),
        "actor": one_line(raw.get("actor"), 80),
        "severity": severity(adjusted_score),
        "score": adjusted_score,
        "initial_score": score,
        "signals": signals,
        "explanations": explanations,
        "benign_context_adjustment": benign_adjustment,
        "detail_sha256": detail_hash,
    }


def build_hypotheses(timeline: list[dict[str, Any]]) -> list[dict[str, Any]]:
    active_signal_set = {
        signal
        for event in timeline
        if not event["benign_context_adjustment"]
        for signal in event["signals"]
    }
    hypotheses: list[dict[str, Any]] = []
    if {"agent_prompt_injection", "wallet_trap"}.intersection(active_signal_set):
        hypotheses.append(
            {
                "id": "agent_tool_abuse",
                "confidence": "high" if "agent_prompt_injection" in active_signal_set else "medium",
                "why": "external content attempted to control the agent or trigger payment-capable approval",
            }
        )
    if {"credential_access", "exfiltration"}.issubset(active_signal_set):
        hypotheses.append(
            {
                "id": "credential_theft_with_exfiltration",
                "confidence": "high",
                "why": "credential material access and outbound transfer appeared in the same host timeline",
            }
        )
    if "encoded_execution" in active_signal_set:
        hypotheses.append(
            {
                "id": "scripted_execution_chain",
                "confidence": "medium",
                "why": "encoded shell activity preceded higher-risk endpoint or network signals",
            }
        )
    return hypotheses


def build_self_corrections(timeline: list[dict[str, Any]]) -> list[dict[str, Any]]:
    corrections = [
        {
            "event_id": event["event_id"],
            "from": "high-risk keyword match",
            "to": "low-risk contextual reference",
            "reason": "source is training or documentation context and no tool side effect occurred",
        }
        for event in timeline
        if event["benign_context_adjustment"]
    ]
    if corrections and any(event["severity"] in {"critical", "high"} for event in timeline):
        corrections.append(
            {
                "event_id": "analysis_loop",
                "from": "keyword-only alerting",
                "to": "sequence-aware investigation",
                "reason": "benign references are kept out of the incident path while real tool and endpoint attacks remain high risk",
            }
        )
    return corrections


def build_response_plan(timeline: list[dict[str, Any]], hypotheses: list[dict[str, Any]]) -> list[dict[str, Any]]:
    high_hosts = sorted(
        {
            event["host"]
            for event in timeline
            if event["host"] and event["severity"] in {"critical", "high"} and not event["benign_context_adjustment"]
        }
    )
    plan = [
        {
            "phase": "triage",
            "action": "rank events by sequence, source, score, and whether a tool side effect was requested",
            "approval_required": False,
        },
        {
            "phase": "scope",
            "action": f"scope affected hosts: {', '.join(high_hosts) or 'none detected'}",
            "approval_required": False,
        },
    ]
    if any(item["id"] == "agent_tool_abuse" for item in hypotheses):
        plan.append(
            {
                "phase": "agent_control",
                "action": "block prompt-exfiltration and wallet-signing lures before shell, browser, git, or wallet tools run",
                "approval_required": False,
            }
        )
    plan.extend(
        [
            {
                "phase": "contain",
                "action": "pause unsafe agent tools and isolate affected endpoint hosts after operator approval",
                "approval_required": True,
            },
            {
                "phase": "recover",
                "action": "restore normal tool access only after policy hooks block replayed probes",
                "approval_required": False,
            },
        ]
    )
    return plan


def build_report(events: list[dict[str, Any]], case_id: str = "rewardops-defender") -> dict[str, Any]:
    timeline = sorted((sanitize_event(event) for event in events), key=lambda item: item["ts"])
    hypotheses = build_hypotheses(timeline)
    signal_counts = Counter(signal for event in timeline for signal in event["signals"])
    high_count = sum(1 for event in timeline if event["severity"] in {"critical", "high"})
    verdict = "+".join(item["id"] for item in hypotheses) or "no_active_intrusion_confirmed"
    return {
        "schema": "rewardops.defender.v1",
        "generated_at": now_iso(),
        "case_id": one_line(case_id, 80),
        "event_count": len(timeline),
        "high_event_count": high_count,
        "verdict": verdict,
        "timeline": timeline,
        "hypotheses": hypotheses,
        "self_corrections": build_self_corrections(timeline),
        "response_plan": build_response_plan(timeline, hypotheses),
        "signal_counts": dict(sorted(signal_counts.items())),
        "raw_text_policy": "raw event details are hashed and not stored",
        "safe_boundaries": [
            "Defensive triage only; no exploitation, live probing, wallet signing, or destructive remediation.",
            "Prompt text, logs, and private artifacts are represented by hashes and structured signals.",
            "Containment or credential rotation recommendations require operator approval.",
        ],
    }


def write_markdown(path: Path, report: dict[str, Any]) -> None:
    lines = [
        "# RewardOps Defender Report",
        "",
        f"Generated: {report['generated_at']}",
        f"Case: {report['case_id']}",
        f"Verdict: {report['verdict']}",
        f"Events: {report['event_count']}",
        f"High/Critical events: {report['high_event_count']}",
        f"Self-corrections: {len(report['self_corrections'])}",
        "",
        "## Hypotheses",
        "",
    ]
    for item in report["hypotheses"]:
        lines.append(f"- {item['confidence'].upper()} {item['id']}: {item['why']}")
    lines.extend(["", "## Timeline", ""])
    for event in report["timeline"]:
        lines.append(
            "- "
            f"{event['ts']} {event['severity'].upper()} {event['host']} "
            f"{event['source']}/{event['event_type']} "
            f"signals={','.join(event['signals']) or 'none'} hash={event['detail_sha256'][:12]}"
        )
    lines.extend(["", "## Response Plan", ""])
    for step in report["response_plan"]:
        approval = "approval-required" if step["approval_required"] else "local-safe"
        lines.append(f"- {step['phase']}: {step['action']} ({approval})")
    lines.extend(["", "Raw event details are intentionally hashed and not stored.", ""])
    path.write_text("\n".join(lines), encoding="utf-8")


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Build a RewardOps Defender report from sanitized events.")
    p.add_argument("--events", type=Path, required=True)
    p.add_argument("--json-output", type=Path, required=True)
    p.add_argument("--markdown-output", type=Path, required=True)
    p.add_argument("--case-id", default="rewardops-defender")
    return p


def main() -> int:
    args = parser().parse_args()
    report = build_report(load_events(args.events), case_id=args.case_id)
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown(args.markdown_output, report)
    print(json.dumps({"event_count": report["event_count"], "high_event_count": report["high_event_count"], "verdict": report["verdict"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Build a deterministic defensive DFIR triage report from sanitized events."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import ipaddress
import json
from pathlib import Path
import re
from typing import Any


EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
TOKEN_RE = re.compile(r"\b(?:sk-[A-Za-z0-9_-]{12,}|[A-Fa-f0-9]{32,})\b")

RULES: list[tuple[str, int, str, str]] = [
    ("encodedcommand", 40, "PowerShell encoded command", "Isolate host and collect PowerShell transcript/logs."),
    ("mimikatz", 70, "Credential dumping indicator", "Reset exposed credentials and inspect LSASS access."),
    ("rundll32", 25, "Living-off-the-land binary", "Validate parent process and loaded DLL path."),
    ("regsvr32", 25, "Living-off-the-land binary", "Validate scriptlet use and outbound traffic."),
    ("failed_login", 15, "Repeated failed login", "Check source reputation and enforce MFA/session review."),
    ("payload.dll", 35, "Suspicious payload write", "Quarantine file and hash it in a sandboxed workflow."),
    ("appdata", 20, "User-profile persistence path", "Review Run keys, startup folders, and scheduled tasks."),
    ("external_connection", 20, "External network connection", "Block destination pending reputation review."),
]
RULE_IDS = {rule[0] for rule in RULES}


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def one_line(value: Any, limit: int = 220) -> str:
    return " ".join(str(value or "").split())[:limit]


def redact(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): redact(v) for k, v in value.items()}
    if isinstance(value, list):
        return [redact(v) for v in value]
    if isinstance(value, str):
        text = EMAIL_RE.sub("[redacted-email]", value)
        return TOKEN_RE.sub("[redacted-token]", text)
    return value


def canonical_hash(event: dict[str, Any]) -> str:
    redacted = redact(event)
    blob = json.dumps(redacted, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def is_non_public_address(value: Any) -> bool:
    text = str(value or "").strip()
    if not text:
        return False
    try:
        addr = ipaddress.ip_address(text)
    except ValueError:
        return text.lower() in {"localhost"}
    return bool(
        addr.is_private
        or addr.is_loopback
        or addr.is_link_local
        or addr.is_multicast
        or addr.is_reserved
        or addr.is_unspecified
    )


def load_events(path: Path) -> list[dict[str, Any]]:
    text = path.read_text(encoding="utf-8")
    stripped = text.strip()
    if not stripped:
        return []
    if stripped.startswith("["):
        data = json.loads(stripped)
        if not isinstance(data, list):
            raise ValueError("JSON input must be an array of events")
        return [item for item in data if isinstance(item, dict)]
    events = []
    for lineno, line in enumerate(text.splitlines(), start=1):
        if not line.strip():
            continue
        item = json.loads(line)
        if not isinstance(item, dict):
            raise ValueError(f"line {lineno} is not an object")
        events.append(item)
    return events


def text_for_rule(event: dict[str, Any]) -> str:
    redacted = redact(event)
    return json.dumps(redacted, sort_keys=True).lower()


def score_event(event: dict[str, Any]) -> dict[str, Any]:
    text = text_for_rule(event)
    findings = []
    score = 0
    for needle, weight, title, recommendation in RULES:
        if needle == "external_connection":
            hit = str(event.get("event_type") or "").lower() in {"network_connection", "dns_query"} and not str(
                event.get("dst") or event.get("domain") or ""
            ).startswith(("10.", "192.168.", "172.16."))
        else:
            hit = needle in text
        if hit:
            score += weight
            findings.append({"rule": needle, "title": title, "weight": weight, "recommendation": recommendation})
    corrections = []
    if any(finding["rule"] == "external_connection" for finding in findings) and is_non_public_address(
        event.get("dst") or event.get("domain")
    ):
        findings = [finding for finding in findings if finding["rule"] != "external_connection"]
        score = sum(finding["weight"] for finding in findings)
        corrections.append(
            {
                "type": "false_positive_removed",
                "rule": "external_connection",
                "reason": "destination is non-public or reserved test evidence, so it is not treated as internet egress",
            }
        )
    return {
        "event_hash": canonical_hash(event),
        "ts": one_line(event.get("ts") or event.get("timestamp") or ""),
        "host": one_line(event.get("host") or event.get("hostname") or ""),
        "event_type": one_line(event.get("event_type") or event.get("type") or ""),
        "score": min(score, 100),
        "findings": findings,
        "corrections": corrections,
        "redacted_event": redact(event),
    }


def severity(total_score: int, max_event_score: int) -> str:
    if total_score >= 120 or max_event_score >= 70:
        return "critical"
    if total_score >= 70 or max_event_score >= 40:
        return "high"
    if total_score >= 30:
        return "medium"
    if total_score > 0:
        return "low"
    return "informational"


def expected_rules(event: dict[str, Any]) -> set[str]:
    raw = event.get("expected_rules") or event.get("expected_findings") or []
    if isinstance(raw, str):
        raw = [part.strip() for part in raw.split(",")]
    if not isinstance(raw, list):
        return set()
    return {str(item) for item in raw if str(item) in RULE_IDS}


def build_accuracy_report(events: list[dict[str, Any]], scored: list[dict[str, Any]]) -> dict[str, Any]:
    labelled = []
    for event, item in zip(events, scored):
        expected = expected_rules(event)
        if not expected:
            continue
        observed = {finding["rule"] for finding in item["findings"]}
        labelled.append(
            {
                "event_hash": item["event_hash"],
                "expected_rules": sorted(expected),
                "observed_rules": sorted(observed),
                "missed_rules": sorted(expected - observed),
                "unexpected_rules": sorted(observed - expected),
            }
        )
    if not labelled:
        return {
            "status": "no_ground_truth_labels",
            "labelled_event_count": 0,
            "precision": None,
            "recall": None,
            "missed_rule_count": 0,
            "unexpected_rule_count": 0,
            "events": [],
        }
    expected_total = sum(len(item["expected_rules"]) for item in labelled)
    observed_total = sum(len(item["observed_rules"]) for item in labelled)
    missed_total = sum(len(item["missed_rules"]) for item in labelled)
    unexpected_total = sum(len(item["unexpected_rules"]) for item in labelled)
    true_positive_total = max(observed_total - unexpected_total, 0)
    precision = true_positive_total / observed_total if observed_total else 1.0
    recall = true_positive_total / expected_total if expected_total else 1.0
    return {
        "status": "validated" if missed_total == 0 and unexpected_total == 0 else "needs_review",
        "labelled_event_count": len(labelled),
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "missed_rule_count": missed_total,
        "unexpected_rule_count": unexpected_total,
        "events": labelled,
    }


def build_report(events: list[dict[str, Any]], case_id: str = "local-case") -> dict[str, Any]:
    scored = [score_event(event) for event in events]
    total = sum(item["score"] for item in scored)
    max_score = max([item["score"] for item in scored] or [0])
    top_recommendations: list[str] = []
    for item in scored:
        for finding in item["findings"]:
            rec = finding["recommendation"]
            if rec not in top_recommendations:
                top_recommendations.append(rec)
    audit_trail = [
        {
            "step": index,
            "event_hash": item["event_hash"],
            "event_type": item["event_type"],
            "matched_rules": [finding["rule"] for finding in item["findings"]],
            "correction_count": len(item["corrections"]),
        }
        for index, item in enumerate(scored, start=1)
    ]
    self_corrections = [
        {"event_hash": item["event_hash"], **correction}
        for item in scored
        for correction in item["corrections"]
    ]
    return {
        "schema": "rewardops.dfir_triage.v1",
        "generated_at": now_iso(),
        "case_id": one_line(case_id, 80),
        "event_count": len(events),
        "total_score": total,
        "max_event_score": max_score,
        "severity": severity(total, max_score),
        "finding_count": sum(len(item["findings"]) for item in scored),
        "timeline": sorted(scored, key=lambda item: item.get("ts") or ""),
        "accuracy_report": build_accuracy_report(events, scored),
        "self_corrections": self_corrections,
        "audit_trail": audit_trail,
        "containment_checklist": top_recommendations
        or ["Preserve logs, confirm scope with the system owner, and avoid destructive remediation before evidence capture."],
        "safe_boundaries": [
            "Defensive triage only; no exploitation, live probing, credential use, or malware execution.",
            "Emails and token-like values are redacted before reporting.",
            "Event hashes are over redacted canonical event data for reproducible evidence tracking.",
        ],
    }


def write_markdown(path: Path, report: dict[str, Any]) -> None:
    lines = [
        "# DFIR Triage Report",
        "",
        f"Generated: {report['generated_at']}",
        f"Case: {report['case_id']}",
        f"Severity: {report['severity']}",
        f"Events: {report['event_count']}",
        f"Findings: {report['finding_count']}",
        "",
        "## Containment Checklist",
        "",
    ]
    lines.extend(f"- {item}" for item in report["containment_checklist"])
    lines.extend(["", "## Timeline", ""])
    for item in report["timeline"]:
        findings = ", ".join(f["title"] for f in item["findings"]) or "no triggered rule"
        lines.append(f"- {item['ts'] or 'unknown time'} `{item['host']}` {item['event_type']}: {findings} ({item['event_hash'][:12]})")
    accuracy = report["accuracy_report"]
    lines.extend(
        [
            "",
            "## Accuracy Report",
            "",
            f"- Status: {accuracy['status']}",
            f"- Labelled events: {accuracy['labelled_event_count']}",
            f"- Precision: {accuracy['precision']}",
            f"- Recall: {accuracy['recall']}",
            f"- Missed rules: {accuracy['missed_rule_count']}",
            f"- Unexpected rules: {accuracy['unexpected_rule_count']}",
            "",
            "## Self-Correction",
            "",
        ]
    )
    if report["self_corrections"]:
        for correction in report["self_corrections"]:
            lines.append(f"- {correction['rule']}: {correction['reason']} ({correction['event_hash'][:12]})")
    else:
        lines.append("- No automatic corrections were needed.")
    lines.extend(["", "## Audit Trail", ""])
    for step in report["audit_trail"]:
        lines.append(
            f"- Step {step['step']}: {step['event_type']} hash={step['event_hash'][:12]} "
            f"rules={','.join(step['matched_rules']) or 'none'} corrections={step['correction_count']}"
        )
    lines.extend(["", "## Safe Boundaries", ""])
    lines.extend(f"- {item}" for item in report["safe_boundaries"])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Build a defensive DFIR triage report from sanitized events.")
    p.add_argument("--events", required=True, type=Path)
    p.add_argument("--json-output", required=True, type=Path)
    p.add_argument("--markdown-output", required=True, type=Path)
    p.add_argument("--case-id", default="local-case")
    return p


def main() -> int:
    args = parser().parse_args()
    report = build_report(load_events(args.events), case_id=args.case_id)
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown(args.markdown_output, report)
    print(json.dumps({"severity": report["severity"], "event_count": report["event_count"], "finding_count": report["finding_count"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

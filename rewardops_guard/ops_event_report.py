#!/usr/bin/env python3
"""Build a sanitized ops/security report from RewardOps event JSONL.

The report is designed for demos and buyer deliverables: it accepts structured
events only, drops unknown/raw-text fields, and emits compact JSON/Markdown that
can be imported into SIEM, workflow, or dashboard tools without leaking prompt
text.
"""

from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
GUARD_DIR = ROOT / "rewardops_guard"
DEFAULT_EVENTS = GUARD_DIR / "ops_events.jsonl"
DEFAULT_JSON = GUARD_DIR / "ops_event_report.json"
DEFAULT_MD = GUARD_DIR / "ops_event_report.md"

ALLOWED_FIELDS = {
    "ts",
    "event_id",
    "source",
    "route",
    "event_type",
    "severity",
    "decision",
    "reward_usd",
    "signals",
    "next_action",
    "evidence_hash",
}

SEVERITY_ORDER = {"critical": 4, "high": 3, "medium": 2, "low": 1, "info": 0}


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def one_line(value: Any, limit: int = 180) -> str:
    return " ".join(str(value or "").split())[:limit]


def money(value: Any) -> float:
    try:
        return round(float(value or 0), 2)
    except (TypeError, ValueError):
        return 0.0


def clean_event(raw: dict[str, Any]) -> dict[str, Any]:
    event = {key: raw.get(key) for key in ALLOWED_FIELDS}
    event["ts"] = one_line(event.get("ts"), 40)
    event["event_id"] = one_line(event.get("event_id"), 80)
    event["source"] = one_line(event.get("source"), 80)
    event["route"] = one_line(event.get("route"), 120)
    event["event_type"] = one_line(event.get("event_type"), 80)
    event["severity"] = one_line(event.get("severity"), 20).lower() or "info"
    event["decision"] = one_line(event.get("decision"), 40)
    event["reward_usd"] = money(event.get("reward_usd"))
    event["signals"] = [one_line(item, 60) for item in (event.get("signals") or [])[:8]]
    event["next_action"] = one_line(event.get("next_action"), 180)
    event["evidence_hash"] = one_line(event.get("evidence_hash"), 80)
    return event


def load_events(path: Path) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    if not path.exists():
        return events
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            raw = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(raw, dict):
            events.append(clean_event(raw))
    return events


def top_events(events: list[dict[str, Any]], limit: int = 12) -> list[dict[str, Any]]:
    return sorted(
        events,
        key=lambda item: (
            SEVERITY_ORDER.get(item.get("severity", "info"), 0),
            item.get("reward_usd", 0),
            item.get("ts", ""),
        ),
        reverse=True,
    )[:limit]


def build_report(events: list[dict[str, Any]]) -> dict[str, Any]:
    by_severity = Counter(event["severity"] for event in events)
    by_decision = Counter(event["decision"] or "UNKNOWN" for event in events)
    by_source = Counter(event["source"] or "unknown" for event in events)
    blocked = [event for event in events if event["decision"] == "BLOCK"]
    review = [event for event in events if event["decision"] == "REVIEW"]
    allow = [event for event in events if event["decision"] == "ALLOW"]
    high_risk = [
        event
        for event in events
        if SEVERITY_ORDER.get(event["severity"], 0) >= SEVERITY_ORDER["high"]
    ]
    return {
        "generated_at": now_iso(),
        "event_count": len(events),
        "blocked_count": len(blocked),
        "review_count": len(review),
        "allow_count": len(allow),
        "high_risk_count": len(high_risk),
        "blocked_reward_usd": round(sum(event["reward_usd"] for event in blocked), 2),
        "review_reward_usd": round(sum(event["reward_usd"] for event in review), 2),
        "allow_reward_usd": round(sum(event["reward_usd"] for event in allow), 2),
        "by_severity": dict(sorted(by_severity.items())),
        "by_decision": dict(sorted(by_decision.items())),
        "top_sources": by_source.most_common(8),
        "top_events": top_events(events),
        "schema": sorted(ALLOWED_FIELDS),
        "raw_text_policy": "raw external task text is not stored",
    }


def write_report(report: dict[str, Any], json_path: Path, md_path: Path) -> None:
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# RewardOps Ops Event Report",
        "",
        f"Generated: {report['generated_at']}",
        f"Events: {report['event_count']}",
        f"Blocked: {report['blocked_count']} (${report['blocked_reward_usd']:.2f})",
        f"Review: {report['review_count']} (${report['review_reward_usd']:.2f})",
        f"Allowed: {report['allow_count']} (${report['allow_reward_usd']:.2f})",
        f"High risk: {report['high_risk_count']}",
        "",
        "## Top Events",
        "",
    ]
    for event in report["top_events"]:
        lines.append(
            "- "
            f"{event['severity'].upper()} {event['decision']} "
            f"${event['reward_usd']:.2f} "
            f"{event['source']} - {event['route']} "
            f"signals={','.join(event['signals']) or 'none'}"
        )
    lines.extend(
        [
            "",
            "## Import Schema",
            "",
            ", ".join(report["schema"]),
            "",
            "Raw external task text is intentionally not stored.",
            "",
        ]
    )
    md_path.write_text("\n".join(lines), encoding="utf-8")


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Build sanitized RewardOps event reports.")
    p.add_argument("--events", default=str(DEFAULT_EVENTS))
    p.add_argument("--output-json", default=str(DEFAULT_JSON))
    p.add_argument("--output-md", default=str(DEFAULT_MD))
    return p


def main() -> int:
    args = parser().parse_args()
    events = load_events(Path(args.events))
    report = build_report(events)
    write_report(report, Path(args.output_json), Path(args.output_md))
    print(
        json.dumps(
            {
                "events": report["event_count"],
                "blocked": report["blocked_count"],
                "review": report["review_count"],
                "output_json": str(Path(args.output_json)),
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

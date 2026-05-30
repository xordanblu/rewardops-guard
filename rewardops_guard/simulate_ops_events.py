#!/usr/bin/env python3
"""Generate sanitized RewardOps demo events from the current strategy board."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]


def find_workspace_root() -> Path:
    for candidate in [ROOT, *ROOT.parents]:
        if (candidate / "live_status" / "goal5000_strategy_board_latest.json").exists():
            return candidate
    return ROOT


WORKSPACE_ROOT = find_workspace_root()
LIVE = WORKSPACE_ROOT / "live_status"
OUT = ROOT / "rewardops_guard" / "ops_events.jsonl"


def read_json(path: Path, fallback: Any) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return fallback


def one_line(value: Any, limit: int = 160) -> str:
    return " ".join(str(value or "").split())[:limit]


def money(value: Any) -> float:
    try:
        return round(float(value or 0), 2)
    except (TypeError, ValueError):
        return 0.0


def evidence_hash(*parts: Any) -> str:
    material = "|".join(str(part or "") for part in parts)
    return hashlib.sha256(material.encode("utf-8")).hexdigest()[:24]


def event(
    *,
    ts: datetime,
    source: str,
    route: str,
    event_type: str,
    severity: str,
    decision: str,
    reward_usd: float,
    signals: list[str],
    next_action: str,
) -> dict[str, Any]:
    eid = evidence_hash(ts.isoformat(), source, route, event_type, decision)
    return {
        "ts": ts.replace(microsecond=0).isoformat(),
        "event_id": eid,
        "source": one_line(source, 80),
        "route": one_line(route, 120),
        "event_type": event_type,
        "severity": severity,
        "decision": decision,
        "reward_usd": money(reward_usd),
        "signals": signals[:8],
        "next_action": one_line(next_action, 180),
        "evidence_hash": eid,
    }


def lane_event(ts: datetime, item: dict[str, Any]) -> dict[str, Any]:
    status = one_line(item.get("queue_status"), 60)
    if "BLOCK" in status or "CLOSED" in status:
        decision = "BLOCK"
        severity = "medium"
    elif "APPROVAL" in status or "PENDING" in status or "WATCH" in status:
        decision = "REVIEW"
        severity = "medium"
    else:
        decision = "ALLOW"
        severity = "low"
    signals = [status.lower()]
    reward = money(item.get("reward_usd"))
    if reward >= 250:
        signals.append("high_value")
    return event(
        ts=ts,
        source=one_line(item.get("source"), 80),
        route=one_line(item.get("title"), 120),
        event_type="money_path_triage",
        severity=severity,
        decision=decision,
        reward_usd=reward,
        signals=signals,
        next_action=one_line(item.get("safe_next_action"), 180),
    )


def synthetic_attack_events(base: datetime) -> list[dict[str, Any]]:
    return [
        event(
            ts=base + timedelta(minutes=1),
            source="hostile_bounty_probe",
            route="internal-instruction exfiltration lure",
            event_type="prompt_injection_block",
            severity="critical",
            decision="BLOCK",
            reward_usd=5000,
            signals=["instruction_exfiltration", "prompt_injection", "raw_text_not_stored"],
            next_action="Reject route and retain only hash/signals for audit.",
        ),
        event(
            ts=base + timedelta(minutes=2),
            source="wallet_flow_probe",
            route="wallet authentication/signature request",
            event_type="wallet_action_hold",
            severity="high",
            decision="BLOCK",
            reward_usd=230,
            signals=["wallet_signing", "exact_approval_required"],
            next_action="Hold until the user gives exact scoped approval for a non-spending auth signature.",
        ),
        event(
            ts=base + timedelta(minutes=3),
            source="social_task_probe",
            route="social proof or engagement task",
            event_type="social_route_block",
            severity="high",
            decision="BLOCK",
            reward_usd=100,
            signals=["user_social_forbidden"],
            next_action="Do not use user social accounts; search non-social payout routes.",
        ),
        event(
            ts=base + timedelta(minutes=4),
            source="hackathon_packet",
            route="local RewardOps Guard submission artifact",
            event_type="local_artifact_ready",
            severity="info",
            decision="ALLOW",
            reward_usd=0,
            signals=["local_only", "no_public_submit"],
            next_action="Use for demos, buyer packets, or hackathon submission after account/rules preflight.",
        ),
    ]


def build_events() -> list[dict[str, Any]]:
    guardian = read_json(LIVE / "money_path_guardian_latest.json", {})
    base = datetime.now(timezone.utc).replace(microsecond=0) - timedelta(minutes=20)
    events = []
    for offset, item in enumerate((guardian.get("queue") or [])[:40]):
        events.append(lane_event(base + timedelta(seconds=offset * 20), item))
    events.extend(synthetic_attack_events(base + timedelta(minutes=15)))
    return events


def main() -> int:
    events = build_events()
    OUT.write_text("\n".join(json.dumps(item, sort_keys=True) for item in events) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(OUT), "events": len(events)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

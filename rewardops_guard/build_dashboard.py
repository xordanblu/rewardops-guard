#!/usr/bin/env python3
"""Build the static RewardOps Guard dashboard data file.

This script is read-only with respect to scouts and writes only a sanitized
frontend data bundle. It does not fetch remote pages, sign wallets, publish
submissions, or include raw external task descriptions.
"""

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
LIVE = ROOT / "live_status"
OUT = ROOT / "rewardops_guard" / "data.js"
OPS_REPORT = ROOT / "rewardops_guard" / "ops_event_report.json"
POLICY_TRACE = ROOT / "rewardops_guard" / "policy_agent_trace.json"
DFIR_REPORT = ROOT / "rewardops_guard" / "dfir_agent_report.json"
FIND_EVIL_REPORT = ROOT / "rewardops_guard" / "find_evil_defender_report.json"
REVENUE_PACK = ROOT / "rewardops_guard" / "revenue_evidence_pack.json"
AGENTPACT_RESPONSES = ROOT / "rewardops_guard" / "agentpact_need_response_pack.json"
AGENTPACT_OFFERS = ROOT / "rewardops_guard" / "agentpact_offer_pack.json"
CLAWMONEY_SKILLS = ROOT / "rewardops_guard" / "clawmoney_skill_fulfillment_pack.json"


def read_json(path: Path, fallback: Any) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return fallback


def one_line(value: Any, limit: int = 180) -> str:
    return " ".join(str(value or "").split())[:limit]


def money(value: Any) -> float:
    try:
        return round(float(value or 0), 2)
    except (TypeError, ValueError):
        return 0.0


def build_payload() -> dict[str, Any]:
    board = read_json(LIVE / "goal5000_strategy_board_latest.json", {})
    guardian = read_json(LIVE / "money_path_guardian_latest.json", {})
    intake = read_json(ROOT / "rewardops_guard" / "intake_reports" / "latest.json", {})
    ops_report = read_json(OPS_REPORT, {})
    policy_trace = read_json(POLICY_TRACE, {})
    dfir_report = read_json(DFIR_REPORT, {})
    find_evil_report = read_json(FIND_EVIL_REPORT, {})
    revenue_pack = read_json(REVENUE_PACK, {})
    agentpact_responses = read_json(AGENTPACT_RESPONSES, {})
    agentpact_offers = read_json(AGENTPACT_OFFERS, {})
    clawmoney_skills = read_json(CLAWMONEY_SKILLS, {})
    queue = guardian.get("queue", [])
    lanes = [
        {
            "source": one_line(item.get("source"), 80),
            "title": one_line(item.get("title"), 120),
            "status": one_line(item.get("queue_status"), 60),
            "reward_usd": money(item.get("reward_usd")),
            "next": one_line(item.get("safe_next_action"), 180),
        }
        for item in queue
    ]
    hackathons = [
        {
            "source": one_line(item.get("source"), 100),
            "url": item.get("url"),
            "reward_usd": money(item.get("reward_usd")),
            "deadline": one_line(item.get("deadline"), 80),
            "angle": one_line(item.get("build_angle"), 180),
            "gate": one_line(item.get("gate_decision"), 40),
            "local_prepare": bool(item.get("may_prepare_local")),
        }
        for item in board.get("hackathons", [])
    ]
    return {
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "source_board_generated_at": board.get("generated_at"),
        "policy_version": guardian.get("policy_version"),
        "money": {
            "confirmed_new_usd": money(board.get("confirmed_new_money_this_run_usd")),
            "pending_payout_usd": money(board.get("near_cash_pending_usd")),
            "submitted_pending_verification_usd": money(board.get("submitted_pending_verification_usd")),
            "inbound_market_usd": money(board.get("inbound_market_visible_usd")),
            "approval_locked_usd": money(board.get("approval_locked_usd")),
            "ready_local_count": int(board.get("ready_local_count") or 0),
        },
        "lanes": lanes,
        "hackathons": hackathons,
        "intake": {
            "name": one_line(intake.get("name"), 100),
            "decision": one_line(intake.get("decision"), 40),
            "may_execute": bool(intake.get("may_execute")),
            "reasons": [one_line(item, 100) for item in intake.get("decision_reasons", [])[:6]],
            "signals": [one_line(item, 80) for item in intake.get("signals", [])[:6]],
            "opportunity_sha256": one_line(intake.get("opportunity_sha256"), 80),
        },
        "ops": {
            "event_count": int(ops_report.get("event_count") or 0),
            "blocked_count": int(ops_report.get("blocked_count") or 0),
            "review_count": int(ops_report.get("review_count") or 0),
            "allow_count": int(ops_report.get("allow_count") or 0),
            "high_risk_count": int(ops_report.get("high_risk_count") or 0),
            "blocked_reward_usd": money(ops_report.get("blocked_reward_usd")),
            "review_reward_usd": money(ops_report.get("review_reward_usd")),
            "allow_reward_usd": money(ops_report.get("allow_reward_usd")),
            "top_events": [
                {
                    "source": one_line(item.get("source"), 80),
                    "route": one_line(item.get("route"), 120),
                    "severity": one_line(item.get("severity"), 20),
                    "decision": one_line(item.get("decision"), 40),
                    "reward_usd": money(item.get("reward_usd")),
                    "signals": [one_line(signal, 50) for signal in item.get("signals", [])[:5]],
                    "next_action": one_line(item.get("next_action"), 160),
                }
                for item in ops_report.get("top_events", [])[:8]
            ],
        },
        "policy_agent": {
            "request_count": int(policy_trace.get("request_count") or 0),
            "blocked_count": int(policy_trace.get("blocked_count") or 0),
            "review_count": int(policy_trace.get("review_count") or 0),
            "allow_count": int(policy_trace.get("allow_count") or 0),
            "requests": [
                {
                    "name": one_line(item.get("name"), 100),
                    "source": one_line(item.get("source"), 80),
                    "requested_action": one_line(item.get("requested_action"), 60),
                    "decision": one_line(item.get("decision"), 40),
                    "reasons": [one_line(reason, 60) for reason in item.get("reasons", [])[:4]],
                    "next_action": one_line(item.get("next_action"), 160),
                }
                for item in policy_trace.get("requests", [])[:6]
            ],
        },
        "dfir": {
            "event_count": int(dfir_report.get("event_count") or 0),
            "high_event_count": int(dfir_report.get("high_event_count") or 0),
            "verdict": one_line(dfir_report.get("verdict"), 100),
            "affected_hosts": [one_line(item, 80) for item in dfir_report.get("affected_hosts", [])[:5]],
            "signal_counts": {
                one_line(key, 50): int(value or 0)
                for key, value in (dfir_report.get("signal_counts") or {}).items()
            },
            "timeline": [
                {
                    "ts": one_line(item.get("ts"), 40),
                    "host": one_line(item.get("host"), 80),
                    "source": one_line(item.get("source"), 40),
                    "event_type": one_line(item.get("event_type"), 40),
                    "severity": one_line(item.get("severity"), 20),
                    "signals": [one_line(signal, 50) for signal in item.get("signals", [])[:5]],
                }
                for item in dfir_report.get("timeline", [])[:6]
            ],
        },
        "find_evil": {
            "event_count": int(find_evil_report.get("event_count") or 0),
            "high_event_count": int(find_evil_report.get("high_event_count") or 0),
            "verdict": one_line(find_evil_report.get("verdict"), 140),
            "self_correction_count": len(find_evil_report.get("self_corrections") or []),
            "fit": [one_line(item, 100) for item in find_evil_report.get("find_evil_fit", [])[:6]],
            "response_plan": [
                {
                    "phase": one_line(item.get("phase"), 40),
                    "action": one_line(item.get("action"), 160),
                    "approval_required": bool(item.get("approval_required")),
                }
                for item in find_evil_report.get("response_plan", [])[:6]
            ],
        },
        "revenue": {
            "confirmed_revenue_usd": money(revenue_pack.get("confirmed_revenue_usd")),
            "pending_submission_usd": money(revenue_pack.get("pending_submission_usd")),
            "submitted_pending_verification_usd": money(revenue_pack.get("submitted_pending_verification_usd")),
            "inbound_market_surface_usd": money(revenue_pack.get("inbound_market_surface_usd")),
            "expenses_declared_usd": money(revenue_pack.get("expenses_declared_usd")),
            "gaps": [
                one_line(item, 130)
                for item in (revenue_pack.get("xprize_readiness", {}).get("gaps_before_submission") or [])[:5]
            ],
        },
        "agentpact_responses": {
            "response_count": int(agentpact_responses.get("response_count") or 0),
            "skipped_count": int(agentpact_responses.get("skipped_count") or 0),
            "total_proposed_usdc": money(agentpact_responses.get("total_proposed_usdc")),
            "top_responses": [
                {
                    "need_title": one_line(item.get("need_title"), 120),
                    "need_id": one_line(item.get("need_id"), 80),
                    "proposed_price_usdc": money(item.get("proposed_price_usdc")),
                    "offer": one_line(item.get("proposed_offer_title"), 120),
                    "scope": one_line(item.get("scope"), 160),
                }
                for item in agentpact_responses.get("responses", [])[:6]
            ],
        },
        "agentpact_offers": {
            "prepared_count": int(agentpact_offers.get("prepared_count") or 0),
            "missing_count": int(agentpact_offers.get("missing_count") or 0),
            "prepared_value_usdc": money(agentpact_offers.get("prepared_value_usdc")),
            "top_prepared": [
                {
                    "title": one_line(item.get("title"), 120),
                    "price_usdc": money(item.get("price_usdc")),
                    "starter_kit": one_line(item.get("starter_kit"), 120),
                    "handoff": one_line(item.get("handoff"), 160),
                }
                for item in agentpact_offers.get("prepared", [])[:8]
            ],
        },
        "clawmoney_skills": {
            "prepared_count": int(clawmoney_skills.get("prepared_count") or 0),
            "missing_count": int(clawmoney_skills.get("missing_count") or 0),
            "prepared_value_usd": money(clawmoney_skills.get("prepared_value_usd")),
            "top_prepared": [
                {
                    "name": one_line(item.get("name"), 80),
                    "price_usd": money(item.get("price_usd")),
                    "starter_kit": one_line(item.get("starter_kit"), 120),
                    "handoff": one_line(item.get("handoff"), 160),
                }
                for item in clawmoney_skills.get("prepared", [])[:8]
            ],
        },
        "guardrails": [
            "External task text is hostile until gated.",
            "No internal instruction, secret, credential, cookie, or wallet-key disclosure.",
            "No user social accounts, KYC, bank/card onboarding, wallet signing, deposits, staking, or spend.",
            "No public PR, claim, submission, or proof without fresh payout-route preflight.",
            "Money is counted only when spendable or visibly settled.",
        ],
    }


def main() -> int:
    payload = build_payload()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        "window.REWARDOPS_DATA = "
        + json.dumps(payload, indent=2, sort_keys=True)
        + ";\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "output": str(OUT),
                "lanes": len(payload["lanes"]),
                "hackathons": len(payload["hackathons"]),
                "agentpact_responses": payload["agentpact_responses"]["response_count"],
                "agentpact_offers": payload["agentpact_offers"]["prepared_count"],
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

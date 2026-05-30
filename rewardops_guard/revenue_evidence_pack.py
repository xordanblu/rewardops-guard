#!/usr/bin/env python3
"""Build a sanitized revenue evidence pack for AI-operated business routes.

This pack is meant for hackathons and buyer diligence that ask for proof of a
real business: revenue, orders, listings, expenses, and agent-operation logs.
It is deliberately evidence-first and does not turn listings into revenue.
"""

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
LIVE = ROOT / "live_status"
OUT_JSON = ROOT / "rewardops_guard" / "revenue_evidence_pack.json"
OUT_MD = ROOT / "rewardops_guard" / "revenue_evidence_pack.md"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def read_json(path: Path, fallback: Any) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return fallback


def one_line(value: Any, limit: int = 180) -> str:
    return " ".join(str(value or "").split())[:limit]


def public_evidence_ref(path: Path | None) -> str | None:
    if not path:
        return None
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return path.name


def redact_public_identifier(value: Any) -> str:
    text = one_line(value, 90)
    if not text:
        return ""
    if text.startswith("0x") and len(text) == 42:
        return f"{text[:6]}...{text[-4:]}"
    if len(text) > 16:
        return f"{text[:6]}...{text[-4:]}"
    return text


def latest_json_file(directory: Path, pattern: str) -> tuple[Path | None, dict[str, Any]]:
    try:
        paths = sorted(directory.glob(pattern), key=lambda p: p.stat().st_mtime, reverse=True)
    except FileNotFoundError:
        return None, {}
    for path in paths:
        data = read_json(path, {})
        if isinstance(data, dict) and data:
            return path, data
    return None, {}


def money(value: Any) -> float:
    try:
        return round(float(value or 0), 2)
    except (TypeError, ValueError):
        return 0.0


def clawlancer_evidence() -> dict[str, Any]:
    data = read_json(LIVE / "clawlancer_200" / "latest.json", {})
    profile = data.get("profile") or {}
    own_listings = data.get("own_listings") or []
    write_actions = [
        item
        for item in data.get("actions") or []
        if str(item.get("action") or "").startswith(("create_", "deliver_", "claim_"))
    ]
    return {
        "own_listing_count": len(own_listings),
        "own_listing_usd": round(sum(money(item.get("price_wei")) / 1_000_000 for item in own_listings), 2),
        "transaction_count": len(data.get("transactions") or []),
        "actions_in_latest_scan": len(write_actions),
        "platform_balance_usd": money(profile.get("platform_balance_wei")) / 1_000_000,
        "total_earned_usd": money(profile.get("total_earned_wei")) / 1_000_000,
        "recent_listings": [
            {
                "title": one_line(item.get("title"), 100),
                "price_usd": round(money(item.get("price_wei")) / 1_000_000, 2),
                "listing_type": one_line(item.get("listing_type"), 30),
            }
            for item in own_listings[:12]
        ],
    }


def clawmoney_evidence() -> dict[str, Any]:
    submissions = read_json(LIVE / "clawmoney_submissions_200" / "latest.json", {})
    skills = read_json(LIVE / "clawmoney_market_skills" / "latest.json", {})
    skill_pack = read_json(ROOT / "rewardops_guard" / "clawmoney_skill_fulfillment_pack.json", {})
    task_budget_by_id = {
        str(item.get("id")): money(item.get("budget"))
        for item in submissions.get("watched_tasks", [])
        if item.get("id")
    }
    pending_submissions = [
        item
        for item in submissions.get("my_submissions", [])
        if str(item.get("status") or "").lower() == "pending"
    ]
    return {
        "pending_submission_count": len(pending_submissions),
        "pending_submission_usd": round(
            sum(
                money(item.get("task_budget") or item.get("payout_amount"))
                or task_budget_by_id.get(str(item.get("task_id")), 0.0)
                for item in pending_submissions
            ),
            2,
        ),
        "paid_or_approved_count": len(
            [
                item
                for item in submissions.get("my_submissions", [])
                if str(item.get("status") or "").lower() in {"paid", "approved", "settled"}
            ]
        ),
        "high_value_skill_count": int(skills.get("count") or 0),
        "high_value_skill_usd": money(skills.get("total_high_value_usd")),
        "prepared_skill_count": int(skill_pack.get("prepared_count") or 0),
        "prepared_skill_usd": money(skill_pack.get("prepared_value_usd")),
        "missing_skill_count": int(skill_pack.get("missing_count") or 0),
        "policy_agent_skill_active": any(
            item.get("name") == "policy-agent-trace"
            for item in skills.get("high_value_active_skills", [])
        ),
    }


def agentpact_evidence() -> dict[str, Any]:
    data = read_json(LIVE / "agentpact_200" / "latest.json", {})
    offer_pack = read_json(ROOT / "rewardops_guard" / "agentpact_offer_pack.json", {})
    offers = data.get("offers") or []
    active_offers = [
        item
        for item in offers
        if str(item.get("status") or item.get("action") or "active").lower() not in {"closed", "cancelled", "expired"}
    ]
    deals = data.get("deals") or {}
    open_deals = deals.get("mine_open") if isinstance(deals, dict) else []
    matches = data.get("matches") or {}
    return {
        "active_offer_count": len(active_offers),
        "active_offer_usd": round(sum(money(item.get("base_price") or item.get("basePrice")) for item in active_offers), 2),
        "match_count": int(matches.get("count") or 0) if isinstance(matches, dict) else 0,
        "open_deal_count": len(open_deals or []),
        "prepared_offer_count": int(offer_pack.get("prepared_count") or 0),
        "prepared_offer_usd": money(offer_pack.get("prepared_value_usdc")),
        "recent_offers": [
            {
                "title": one_line(item.get("title"), 100),
                "price_usd": money(item.get("base_price") or item.get("basePrice")),
                "currency": one_line(item.get("currency") or "USDC", 20),
            }
            for item in active_offers[:12]
        ],
    }


def bountybook_evidence() -> dict[str, Any]:
    data = read_json(LIVE / "bountybook_payout_verifier_200" / "latest.json", {})
    attempt_audit = read_json(LIVE / "bountybook_attempt_audit_200" / "latest.json", {})
    balances = data.get("balances") or {}
    nominal_submitted = money(data.get("nominal_submitted_usdc"))
    nominal_failed = money(attempt_audit.get("nominal_failed_usdc"))
    audit_submitted_count = int(attempt_audit.get("submitted_count") or 0)
    payout_submitted_count = int(data.get("submitted_count") or 0)
    audit_applies = bool(audit_submitted_count and audit_submitted_count == payout_submitted_count)
    failed_count = int(attempt_audit.get("our_failed_count") or 0)
    passed_count = int(attempt_audit.get("our_passed_count") or 0)
    failure_reasons = {
        one_line((attempt or {}).get("reason"), 160)
        for row in attempt_audit.get("failed", [])
        for attempt in (row.get("our_attempts") or [])
        if isinstance(row, dict)
    }
    oracle_unhealthy = failed_count >= 10 and passed_count == 0 and any(
        "Cannot read properties of undefined" in reason or "Code output too small" in reason
        for reason in failure_reasons
    )
    pending_after_audit = 0.0 if oracle_unhealthy else max(0.0, nominal_submitted - nominal_failed) if audit_applies else nominal_submitted
    return {
        "submitted_count": payout_submitted_count,
        "submitted_pending_verification_usd": pending_after_audit,
        "payout_verifier_pending_count": int(data.get("pending_count") or 0),
        "attempt_audit_failed_count": failed_count,
        "attempt_audit_failed_usd": nominal_failed,
        "attempt_audit_passed_count": passed_count,
        "attempt_audit_passed_usd": money(attempt_audit.get("nominal_passed_usdc")),
        "oracle_unhealthy": oracle_unhealthy,
        "failure_reasons": sorted(failure_reasons)[:8],
        "verified_waiting_payout_usd": money(data.get("nominal_verified_waiting_payout_usdc")),
        "paid_or_tx_usd": money(data.get("nominal_paid_or_tx_usdc")),
        "executor_wallet": redact_public_identifier(data.get("executor_wallet")),
        "target_user_wallet": redact_public_identifier(data.get("target_user_wallet")),
        "executor_base_usdc": money(balances.get("executor_base_usdc")),
        "user_base_usdc": money(balances.get("user_base_usdc")),
        "counting_policy": "Submitted BountyBook deliverables are not revenue until verification, payout transaction, or spendable USDC balance is visible; failed attempt-audit rows are treated as non-cashable.",
    }


def settled_wallet_evidence() -> dict[str, Any]:
    path, data = latest_json_file(LIVE / "reward_ops_200", "snapshot_*.json")
    wallets = data.get("wallets") or {}
    user_base_usdc = money(wallets.get("user_base_usdc"))
    return {
        "confirmed_user_base_usdc": user_base_usdc,
        "user_base_wallet": redact_public_identifier(wallets.get("user_base_wallet")),
        "agenthansa_source_usdc": money(wallets.get("agenthansa_source_usdc")),
        "agenthansa_source_wallet": redact_public_identifier(wallets.get("agenthansa_source_wallet")),
        "evidence_source": public_evidence_ref(path),
    }


def build_pack() -> dict[str, Any]:
    board = read_json(LIVE / "goal5000_strategy_board_latest.json", {})
    guardian = read_json(LIVE / "money_path_guardian_latest.json", {})
    policy_trace = read_json(ROOT / "rewardops_guard" / "policy_agent_trace.json", {})
    ops_report = read_json(ROOT / "rewardops_guard" / "ops_event_report.json", {})
    cl = clawlancer_evidence()
    cm = clawmoney_evidence()
    ap = agentpact_evidence()
    bb = bountybook_evidence()
    wallet = settled_wallet_evidence()
    board_submitted_pending = money(board.get("submitted_pending_verification_usd"))
    submitted_pending_after_audit = max(
        bb["submitted_pending_verification_usd"],
        round(max(0.0, board_submitted_pending - bb["attempt_audit_failed_usd"]), 2),
    )
    confirmed_revenue = max(
        money(board.get("confirmed_new_money_this_run_usd")),
        money((board.get("settled_money") or {}).get("confirmed_user_base_usdc")),
        wallet["confirmed_user_base_usdc"],
        bb["user_base_usdc"],
    )
    revenue_gap = round(max(0.0, 5000.0 - confirmed_revenue), 2)
    pack = {
        "generated_at": now_iso(),
        "business_name": "RewardOps Guard",
        "business_category": "AI-operated small-business service for safe agent work intake and revenue operations",
        "confirmed_revenue_usd": confirmed_revenue,
        "goal_gap_usd": revenue_gap,
        "pending_submission_usd": money(board.get("near_cash_pending_usd")),
        "submitted_pending_verification_usd": submitted_pending_after_audit,
        "inbound_market_surface_usd": money(board.get("inbound_market_visible_usd")),
        "approval_locked_usd": money(board.get("approval_locked_usd")),
        "expenses_declared_usd": 0.0,
        "revenue_counting_policy": "Only settled/spendable funds count as revenue; listings and pending submissions are evidence, not revenue.",
        "clawlancer": cl,
        "clawmoney": cm,
        "bountybook": bb,
        "agentpact": ap,
        "settled_wallet": wallet,
        "agent_operations": {
            "policy_trace_requests": int(policy_trace.get("request_count") or 0),
            "policy_trace_blocked": int(policy_trace.get("blocked_count") or 0),
            "ops_event_count": int(ops_report.get("event_count") or 0),
            "ops_high_risk_count": int(ops_report.get("high_risk_count") or 0),
            "guardian_queue_count": len(guardian.get("queue") or []),
        },
        "xprize_readiness": {
            "source": "Build with Gemini XPRIZE",
            "local_prepare_only": True,
            "met_now": [
                "Agent-operation logs exist.",
                "Dashboard screenshots exist.",
                "Marketplace listings and skills are active.",
                "Expenses are tracked as zero for this local phase.",
                "Settled Base USDC evidence exists in the target wallet." if confirmed_revenue > 0 else "No settled revenue is claimed yet.",
            ],
            "gaps_before_submission": [
                f"Settled revenue is currently ${confirmed_revenue:.2f}, still ${revenue_gap:.2f} below the $5,000 goal.",
                "No real customer order has arrived yet.",
                "Google Cloud product usage evidence is not integrated yet.",
                "No public repo, demo video, Devpost account action, or customer contact evidence is approved.",
            ],
        },
    }
    return pack


def write_pack(pack: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(pack, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# RewardOps Revenue Evidence Pack",
        "",
        f"Generated: {pack['generated_at']}",
        f"Business: {pack['business_name']}",
        f"Confirmed revenue: ${pack['confirmed_revenue_usd']:.2f}",
        f"Gap to $5000: ${pack['goal_gap_usd']:.2f}",
        f"Pending submissions: ${pack['pending_submission_usd']:.2f}",
        f"Submitted pending verification: ${pack['submitted_pending_verification_usd']:.2f}",
        f"Inbound market surface: ${pack['inbound_market_surface_usd']:.2f}",
        f"Approval-locked work: ${pack['approval_locked_usd']:.2f}",
        f"Declared expenses: ${pack['expenses_declared_usd']:.2f}",
        "",
        "## Evidence",
        "",
        f"- Clawlancer own listings: {pack['clawlancer']['own_listing_count']} (${pack['clawlancer']['own_listing_usd']:.2f})",
        f"- ClawMoney high-value skills: {pack['clawmoney']['high_value_skill_count']} (${pack['clawmoney']['high_value_skill_usd']:.2f})",
        f"- AgentPact active offers: {pack['agentpact']['active_offer_count']} (${pack['agentpact']['active_offer_usd']:.2f})",
        f"- AgentPact prepared fulfillment packs: {pack['agentpact']['prepared_offer_count']} (${pack['agentpact']['prepared_offer_usd']:.2f})",
        f"- AgentPact matches/open deals: {pack['agentpact']['match_count']} matches, {pack['agentpact']['open_deal_count']} open deals",
        f"- Target wallet settled USDC: ${pack['settled_wallet']['confirmed_user_base_usdc']:.2f}",
        f"- ClawMoney pending submissions: {pack['clawmoney']['pending_submission_count']} (${pack['clawmoney']['pending_submission_usd']:.2f})",
        f"- BountyBook submitted pending verification: {pack['bountybook']['submitted_count']} (${pack['bountybook']['submitted_pending_verification_usd']:.2f})",
        f"- BountyBook failed/non-cashable by attempt audit: {pack['bountybook']['attempt_audit_failed_count']} (${pack['bountybook']['attempt_audit_failed_usd']:.2f})",
        f"- BountyBook paid/tx seen: ${pack['bountybook']['paid_or_tx_usd']:.2f}; executor wallet USDC: ${pack['bountybook']['executor_base_usdc']:.2f}",
        f"- Policy trace requests: {pack['agent_operations']['policy_trace_requests']}",
        f"- Ops events: {pack['agent_operations']['ops_event_count']}",
        "",
        "## Submission Gaps",
        "",
        *[f"- {item}" for item in pack["xprize_readiness"]["gaps_before_submission"]],
        "",
        "Listings and pending submissions are not counted as earned revenue.",
        "",
    ]
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    pack = build_pack()
    write_pack(pack)
    print(
        json.dumps(
            {
                "output_json": str(OUT_JSON),
                "confirmed_revenue_usd": pack["confirmed_revenue_usd"],
                "pending_submission_usd": pack["pending_submission_usd"],
                "submitted_pending_verification_usd": pack["submitted_pending_verification_usd"],
                "inbound_market_surface_usd": pack["inbound_market_surface_usd"],
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

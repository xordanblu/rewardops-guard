#!/usr/bin/env python3
"""Build sanitized hackathon submission packets from local RewardOps evidence.

The builder creates public-submission-ready drafts, not public submissions. It
keeps every external action behind a hold gate because live account, payout,
repo, and video requirements must be rechecked immediately before submission.
"""

from __future__ import annotations

from datetime import datetime, timezone
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
OUT_JSON = ROOT / "rewardops_guard" / "hackathon_submission_pack.json"
OUT_MD = ROOT / "rewardops_guard" / "hackathon_submission_pack.md"


ROUTES: list[dict[str, Any]] = [
    {
        "id": "google_rapid_agent",
        "name": "Google Cloud Rapid Agent Hackathon",
        "url": "https://rapid-agent.devpost.com/",
        "deadline": "2026-06-11 14:00 PDT",
        "cash_surface_usd": 60000,
        "target_prize_usd": 5000,
        "track": "Elastic or GitLab partner track",
        "fit": "Gemini-powered security operations agent for unsafe paid-work and tool-use triage.",
        "pitch": "RewardOps Guard turns untrusted bounty and marketplace prompts into a Gemini-ready security queue with auditable decisions.",
        "requires": [
            "Devpost submission",
            "Google Cloud/Gemini setup",
            "Partner MCP integration",
            "Hosted project URL",
            "Public source repository",
            "Demo video",
        ],
    },
    {
        "id": "find_evil",
        "name": "FIND EVIL!",
        "url": "https://findevil.devpost.com/",
        "deadline": "2026-06-15 23:45 EDT",
        "cash_surface_usd": 22000,
        "target_prize_usd": 10000,
        "track": "Defensive agent / MCP / multi-agent security workflow",
        "fit": "Agent-threat defender that blocks prompt injection, wallet-sign traps, and unsafe external actions.",
        "pitch": "RewardOps Guard finds malicious paid-work prompts before autonomous agents can leak secrets or execute unsafe actions.",
        "requires": [
            "Devpost submission",
            "Public source repository",
            "Demo video",
            "Public project description",
        ],
        "local_artifacts": [
            "rewardops_guard/find_evil_defender_demo.py",
            "rewardops_guard/find_evil_defender_report.md",
            "rewardops_guard/dfir_agent_demo.py",
            "rewardops_guard/policy_agent_trace.md",
            "safety_gate/protective_pipeline.py",
        ],
    },
    {
        "id": "uipath_agenthack",
        "name": "UiPath AgentHack",
        "url": "https://uipath-agenthack.devpost.com/",
        "deadline": "2026-06-29 23:45 PDT",
        "cash_surface_usd": 50000,
        "target_prize_usd": 8000,
        "track": "Maestro Case or Test Cloud",
        "fit": "Human-in-the-loop case workflow for autonomous coding-agent intake, test risk, and payout-route approval.",
        "pitch": "RewardOps Guard gives UiPath a governance case flow for coding agents that chase paid work safely.",
        "requires": [
            "Devpost submission",
            "UiPath Automation Cloud or Labs access",
            "Public source repository",
            "Demo video",
            "Presentation deck",
        ],
    },
    {
        "id": "splunk_agentic_ops",
        "name": "Splunk Agentic Ops Hackathon",
        "url": "https://splunk.devpost.com/",
        "deadline": "2026-06-15 09:00 PDT",
        "cash_surface_usd": 20000,
        "target_prize_usd": 10000,
        "track": "Security or platform/developer experience",
        "fit": "SIEM-ready event stream and analyst workflow for agent prompt-injection and unsafe-tool events.",
        "pitch": "RewardOps Guard ships agent-risk telemetry that Splunk can ingest, investigate, and escalate.",
        "requires": [
            "Devpost submission",
            "Splunk setup or developer license",
            "Public source repository",
            "Demo video",
        ],
    },
    {
        "id": "hedera_enterprise_policy_plugin",
        "name": "Hedera AI Agent Bounty",
        "url": "https://ai-bounties.hedera.com/",
        "deadline": "2026-05-31 23:59 UTC for Week 2",
        "cash_surface_usd": 750,
        "target_prize_usd": 750,
        "track": "Week 2 Enterprise Agent + Plugin",
        "fit": "Enterprise policy plugin for Hedera Agent Kit tool calls.",
        "pitch": "Hedera Enterprise Policy Plugin gates transaction-capable agent tools with deterministic allow/review/block decisions and HCS-ready audit payloads.",
        "requires": [
            "Public source repository",
            "Demo URL or video",
            "Winner payout wallet address",
            "Hedera tool feedback",
            "Submission form",
        ],
        "local_artifacts": [
            "hedera_enterprise_policy_plugin/README.md",
            "hedera_enterprise_policy_plugin/assets/hedera-enterprise-policy-plugin-tile.png",
            "hedera_enterprise_policy_plugin/site/index.html",
            "hedera_enterprise_policy_plugin/src/policy.js",
            "hedera_enterprise_policy_plugin/src/hederaAgentKitAdapter.js",
            "hedera_enterprise_policy_plugin/submission/HEDERA_BOUNTY_SUBMISSION.md",
        ],
    },
    {
        "id": "hedera_policy_agent",
        "name": "Hedera AI Agent Bounty",
        "url": "https://ai-bounties.hedera.com/",
        "deadline": "2026-06-21 23:59 UTC final close",
        "cash_surface_usd": 4750,
        "target_prize_usd": 1500,
        "track": "Week 5 Policy Agent",
        "fit": "Explicit-consent policy layer for payment-capable HBAR/USDC agents.",
        "pitch": "RewardOps Guard is a policy agent that refuses wallet, spend, and secret-disclosure actions without scoped approval.",
        "requires": [
            "Public source repository",
            "Demo URL or video",
            "Winner payout wallet address",
            "Hedera tool feedback",
        ],
    },
]


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def read_json(path: Path, fallback: Any) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return fallback


def money(value: Any) -> float:
    try:
        return round(float(value or 0), 2)
    except (TypeError, ValueError):
        return 0.0


def one_line(value: Any, limit: int = 180) -> str:
    return " ".join(str(value or "").split())[:limit]


def evidence_summary() -> dict[str, Any]:
    revenue = read_json(ROOT / "rewardops_guard" / "revenue_evidence_pack.json", {})
    ops = read_json(ROOT / "rewardops_guard" / "ops_event_report.json", {})
    policy = read_json(ROOT / "rewardops_guard" / "policy_agent_trace.json", {})
    find_evil = read_json(ROOT / "rewardops_guard" / "find_evil_defender_report.json", {})
    strategy = read_json(WORKSPACE_ROOT / "live_status" / "goal5000_strategy_board_latest.json", {})
    return {
        "confirmed_revenue_usd": money(revenue.get("confirmed_revenue_usd")),
        "goal_gap_usd": money(revenue.get("goal_gap_usd")),
        "pending_submission_usd": money(revenue.get("pending_submission_usd")),
        "inbound_market_surface_usd": money(revenue.get("inbound_market_surface_usd")),
        "ops_event_count": int(ops.get("event_count") or 0),
        "ops_blocked_count": int(ops.get("blocked_count") or 0),
        "ops_high_risk_count": int(ops.get("high_risk_count") or 0),
        "policy_request_count": int(policy.get("request_count") or 0),
        "policy_blocked_count": int(policy.get("blocked_count") or 0),
        "find_evil_event_count": int(find_evil.get("event_count") or 0),
        "find_evil_high_event_count": int(find_evil.get("high_event_count") or 0),
        "find_evil_self_corrections": len(find_evil.get("self_corrections") or []),
        "find_evil_verdict": one_line(find_evil.get("verdict"), 180),
        "ready_local_count": int(strategy.get("ready_local_count") or 0),
        "artifact_refs": [
            "rewardops_guard/index.html",
            "rewardops_guard/data.js",
            "rewardops_guard/ops_events.jsonl",
            "rewardops_guard/ops_event_report.md",
            "rewardops_guard/policy_agent_trace.md",
            "rewardops_guard/find_evil_defender_report.md",
            "rewardops_guard/revenue_evidence_pack.md",
            "rewardops_guard/splunk_detection_pack.md",
            "safety_gate/protective_pipeline.py",
        ],
    }


def route_score(route: dict[str, Any]) -> tuple[float, float]:
    """Sort by realistic $5k target first, then total cash surface."""
    target = money(route.get("target_prize_usd"))
    viable_target_bonus = 1 if target >= 5000 else 0
    return (viable_target_bonus, target, money(route.get("cash_surface_usd")))


def build_packet() -> dict[str, Any]:
    evidence = evidence_summary()
    routes = []
    for route in sorted(ROUTES, key=route_score, reverse=True):
        routes.append(
            {
                **route,
                "submission_title": f"RewardOps Guard for {route['name']}",
                "external_action_gate": "HOLD_PUBLIC_SUBMISSION",
                "may_prepare_local": True,
                "revenue_claim": (
                    "No settled revenue is claimed. Pending submissions and inbound listings are evidence only."
                    if evidence["confirmed_revenue_usd"] == 0
                    else (
                        f"${evidence['confirmed_revenue_usd']:.2f} settled revenue is claimed only from wallet/balance "
                        "evidence; pending submissions and inbound listings remain evidence only."
                    )
                ),
                "demo_outline": [
                    "Show the dashboard money queue and active guardrails.",
                    "Run a hostile prompt-injection intake and show BLOCK quorum.",
                    "Show wallet/social/payment lures held before any external action.",
                    "Show SIEM-style evidence and revenue separation.",
                    "Close with exact external submission blockers still held.",
                ],
                "local_artifacts": route.get("local_artifacts", []),
            }
        )
    return {
        "generated_at": now_iso(),
        "product": "RewardOps Guard",
        "objective": "Package a local defensive agent demo for cash-prize routes without making public submissions.",
        "evidence": evidence,
        "routes": routes,
        "submission_boundary": [
            "No Devpost/lablab/forum submission is performed by this packet.",
            "No public repository, public PR, social post, or demo video is published here.",
            "No KYC, payment setup, wallet signing, account creation, paid API spend, or user social account use is authorized here.",
            "All live rules, payout routes, and account requirements must be rechecked before external action.",
        ],
    }


def write_markdown(packet: dict[str, Any]) -> None:
    evidence = packet["evidence"]
    lines = [
        "# RewardOps Hackathon Submission Pack",
        "",
        f"Generated: {packet['generated_at']}",
        "",
        "## Evidence Summary",
        "",
        f"- Confirmed revenue: ${evidence['confirmed_revenue_usd']:.2f}",
        f"- Gap to $5000: ${evidence['goal_gap_usd']:.2f}",
        f"- Pending submissions: ${evidence['pending_submission_usd']:.2f}",
        f"- Inbound market surface: ${evidence['inbound_market_surface_usd']:.2f}",
        f"- Ops events: {evidence['ops_event_count']} ({evidence['ops_blocked_count']} blocked, {evidence['ops_high_risk_count']} high risk)",
        f"- Policy requests: {evidence['policy_request_count']} ({evidence['policy_blocked_count']} blocked)",
        f"- FIND EVIL defender: {evidence['find_evil_event_count']} events, {evidence['find_evil_high_event_count']} high risk, {evidence['find_evil_self_corrections']} self-corrections",
        f"- Ready local lanes: {evidence['ready_local_count']}",
        "",
        "## Ranked Routes",
        "",
    ]
    for route in packet["routes"]:
        lines.extend(
            [
                f"### {route['name']}",
                "",
                f"- URL: {route['url']}",
                f"- Deadline: {route['deadline']}",
                f"- Cash surface: ${money(route['cash_surface_usd']):.0f}",
                f"- Target prize: ${money(route['target_prize_usd']):.0f}",
                f"- Track: {route['track']}",
                f"- Pitch: {route['pitch']}",
                f"- Fit: {route['fit']}",
                f"- Gate: {route['external_action_gate']}",
                f"- Revenue claim: {route['revenue_claim']}",
                "- Required before external submission:",
                *[f"  - {one_line(item)}" for item in route["requires"]],
                "",
            ]
        )
    lines.extend(["## Artifact Refs", ""])
    lines.extend(f"- `{ref}`" for ref in evidence["artifact_refs"])
    lines.extend(["", "## Submission Boundary", ""])
    lines.extend(f"- {item}" for item in packet["submission_boundary"])
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    packet = build_packet()
    OUT_JSON.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown(packet)
    print(
        json.dumps(
            {
                "output_json": str(OUT_JSON),
                "output_md": str(OUT_MD),
                "routes": len(packet["routes"]),
                "top_route": packet["routes"][0]["id"] if packet["routes"] else None,
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

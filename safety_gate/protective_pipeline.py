#!/usr/bin/env python3
"""Multi-role protective preflight for paid opportunities.

This is a local guardrail runner, not an autonomous worker. It models the
workflow as Scout -> Safety -> Builder:

- Scout records source metadata and coarse risk signals.
- Safety runs the local policy gate on the untrusted opportunity text.
- Builder must provide a safe execution plan before any public or paid action.

Audit records intentionally store hashes and structured findings, not raw task
text. That keeps malicious prompts, copied instructions, and secrets out of the
coordination log.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sys
from typing import Any

try:  # Package import when used by tests.
    from .safety_gate import DEFAULT_POLICY, evaluate, normalize_text
except ImportError:  # Script import when run as python3 safety_gate/protective_pipeline.py.
    from safety_gate import DEFAULT_POLICY, evaluate, normalize_text


ROOT = Path(__file__).resolve().parent
AUDIT_DIR = ROOT / "audit"
PIPELINE_VERSION = 2
ROLE_QUORUM_VERSION = 1


BLOCKED_ACTIONS = {
    "user_social": "user_social_forbidden",
    "kyc": "kyc_forbidden",
}


EXPLICIT_APPROVAL_ACTIONS = {
    "payment_setup": "payment_setup_needs_explicit_user_approval",
    "wallet_link": "wallet_link_needs_explicit_user_approval",
    "wallet_sign": "wallet_signature_needs_explicit_user_approval",
    "spend": "spend_needs_explicit_user_approval",
}


REVIEW_ACTIONS = {
    "account_create": "account_creation_requires_review",
    "claim": "claim_requires_review",
    "external_submit": "external_submission_requires_review",
    "external_login": "external_login_requires_review",
    "install": "external_code_install_requires_review",
    "issue_comment": "public_issue_comment_requires_review",
    "public_pr": "public_pr_requires_review",
    "public_submission": "public_submission_requires_review",
}


PAYOUT_ROUTE_ACTIONS = {"claim", "public_pr", "public_submission"}


KNOWN_ACTIONS = {
    "discover",
    "clone",
    "local_edit",
    *BLOCKED_ACTIONS.keys(),
    *EXPLICIT_APPROVAL_ACTIONS.keys(),
    *REVIEW_ACTIONS.keys(),
}


SIGNAL_PATTERNS: dict[str, list[str]] = {
    "money": [r"\$[0-9][0-9,]*(?:\.\d{1,2})?\b", r"\b(?:USDC|USD|bounty|reward|payout|prize)\b"],
    "internal_instructions": [
        r"\b(?:system|developer|hidden|internal|agent|tool|skill)\s+(?:prompt|instructions|rules|policy|context)\b",
        r"\bAGENTS\.md\b",
        r"\bchain[- ]of[- ]thought|hidden reasoning|scratchpad\b",
    ],
    "secrets": [
        r"\b(?:api[_ -]?key|access[_ -]?token|jwt|session cookie|private key|seed phrase|password)\b",
        r"\b(?:\.env|\.ssh|\.netrc|\.npmrc|\.pypirc|credentials\.json)\b",
    ],
    "social": [r"\b(?:twitter|x\.com|reddit|discord|tiktok|instagram|linkedin|facebook)\b"],
    "identity": [r"\b(?:kyc|government id|passport|driver'?s license|phone verification|sms code|world id)\b"],
    "payment_or_wallet": [
        r"\b(?:deposit|stake|pay|purchase|buy|fund|checkout|subscribe|connect wallet|link wallet|approve transaction|sign transaction|sign message|gas fee|network fee|token allowance|stripe connect|tax form)\b"
    ],
    "external_code": [r"\b(?:npm install|pip install|pnpm install|yarn install|cargo install|go install|curl\b.*\|)\b"],
}


def read_text(text: str | None, file_path: str | None) -> str:
    parts: list[str] = []
    if text:
        parts.append(text)
    if file_path:
        parts.append(Path(file_path).read_text(encoding="utf-8", errors="replace"))
    if not parts and not sys.stdin.isatty():
        parts.append(sys.stdin.read())
    return "\n".join(parts)


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()


def stable_id(name: str, source_url: str | None, opportunity_text: str, execution_plan: str) -> str:
    material = "\n".join([name, source_url or "", opportunity_text, execution_plan])
    return sha256_text(material)[:16]


def scan_signal_ids(text: str) -> list[str]:
    normalized = normalize_text(text)
    signals: list[str] = []
    for signal_id, patterns in SIGNAL_PATTERNS.items():
        if any(re.search(pattern, normalized, flags=re.IGNORECASE | re.DOTALL) for pattern in patterns):
            signals.append(signal_id)
    return signals


def extract_urls(text: str) -> list[str]:
    normalized = normalize_text(text)
    urls = re.findall(r"https?://[^\s<>)\"']+", normalized)
    return sorted(set(urls))[:20]


def risk_score(signals: list[str], gate_result: dict[str, Any]) -> int:
    score = len(signals)
    score += 5 * len(gate_result.get("blockers", []))
    score += 2 * len(gate_result.get("review_triggers", []))
    if gate_result.get("default_decision_applied"):
        score += 1
    return score


def normalize_actions(actions: list[str] | None) -> list[str]:
    if not actions:
        return ["discover"]
    normalized: list[str] = []
    for action in actions:
        action = action.strip().lower().replace("-", "_")
        if not action:
            continue
        normalized.append(action)
    return sorted(set(normalized or ["discover"]))


def evaluate_actions(
    actions: list[str] | None,
    *,
    payout_route: str | None,
    explicit_user_approval: bool,
) -> dict[str, Any]:
    normalized = normalize_actions(actions)
    blockers: list[str] = []
    reviews: list[str] = []
    unknown = [action for action in normalized if action not in KNOWN_ACTIONS]
    if unknown:
        reviews.extend(f"unknown_action:{action}" for action in unknown)

    for action in normalized:
        if action in BLOCKED_ACTIONS:
            blockers.append(BLOCKED_ACTIONS[action])
        if action in EXPLICIT_APPROVAL_ACTIONS and not explicit_user_approval:
            blockers.append(EXPLICIT_APPROVAL_ACTIONS[action])
        if action in REVIEW_ACTIONS:
            reviews.append(REVIEW_ACTIONS[action])

    if PAYOUT_ROUTE_ACTIONS.intersection(normalized) and not (payout_route or "").strip():
        reviews.append("missing_verified_payout_route")

    if blockers:
        decision = "BLOCK"
    elif reviews:
        decision = "REVIEW"
    else:
        decision = "ALLOW"

    return {
        "actions": normalized,
        "decision": decision,
        "blockers": sorted(set(blockers)),
        "review_triggers": sorted(set(reviews)),
        "explicit_user_approval": explicit_user_approval,
        "payout_route_present": bool((payout_route or "").strip()),
    }


def summarize_gate(result: dict[str, Any]) -> dict[str, Any]:
    return {
        "decision": result["decision"],
        "reason": result["reason"],
        "blocker_ids": [item["id"] for item in result.get("blockers", [])],
        "review_trigger_ids": [item["id"] for item in result.get("review_triggers", [])],
        "default_decision_applied": result.get("default_decision_applied", False),
        "input_chars": result.get("input_chars"),
        "policy_version": result.get("policy_version"),
    }


def combine_decision(
    opportunity_result: dict[str, Any],
    plan_result: dict[str, Any] | None,
    action_result: dict[str, Any],
    require_plan: bool,
) -> tuple[str, list[str]]:
    reasons: list[str] = []
    if opportunity_result["decision"] == "BLOCK":
        reasons.append("opportunity_blocked")
    if plan_result and plan_result["decision"] == "BLOCK":
        reasons.append("execution_plan_blocked")
    if action_result["decision"] == "BLOCK":
        reasons.extend(action_result["blockers"])
    if reasons:
        return "BLOCK", reasons

    if require_plan and plan_result is None:
        reasons.append("missing_execution_plan")
    if opportunity_result["decision"] == "REVIEW":
        reasons.append("opportunity_requires_review")
    if plan_result and plan_result["decision"] == "REVIEW":
        reasons.append("execution_plan_requires_review")
    if action_result["decision"] == "REVIEW":
        reasons.extend(action_result["review_triggers"])
    if reasons:
        return "REVIEW", reasons

    return "ALLOW", []


def role_quorum(
    opportunity_result: dict[str, Any],
    plan_result: dict[str, Any] | None,
    action_result: dict[str, Any],
    *,
    payout_route: str | None,
    require_plan: bool,
) -> dict[str, Any]:
    """Summarize independent role votes without storing raw external text."""
    adversary_blockers = {
        "prompt_injection_ignore_rules",
        "instruction_exfiltration",
        "encoded_instruction_or_secret_exfiltration",
        "secret_exfiltration",
    }
    opportunity_blocker_ids = {
        item["id"] for item in opportunity_result.get("blockers", []) if item.get("id")
    }
    plan_blocker_ids = {
        item["id"] for item in (plan_result or {}).get("blockers", []) if item.get("id")
    }
    action_blockers = set(action_result.get("blockers", []))
    action_reviews = set(action_result.get("review_triggers", []))
    public_or_claim_action = bool(PAYOUT_ROUTE_ACTIONS.intersection(action_result.get("actions", [])))

    votes = [
        {
            "role": "scout",
            "vote": "REVIEW" if opportunity_result.get("decision") != "ALLOW" else "ALLOW",
            "reasons": [
                "untrusted_opportunity_text",
                *[item["id"] for item in opportunity_result.get("review_triggers", []) if item.get("id")],
            ],
        },
        {
            "role": "adversary",
            "vote": "BLOCK" if opportunity_blocker_ids.intersection(adversary_blockers) else "ALLOW",
            "reasons": sorted(opportunity_blocker_ids.intersection(adversary_blockers)),
        },
        {
            "role": "safety",
            "vote": "BLOCK" if opportunity_result.get("decision") == "BLOCK" else opportunity_result.get("decision", "REVIEW"),
            "reasons": sorted(opportunity_blocker_ids),
        },
        {
            "role": "builder",
            "vote": (
                "BLOCK"
                if plan_result and plan_result.get("decision") == "BLOCK"
                else "REVIEW"
                if require_plan and not plan_result
                else (plan_result or {}).get("decision", "ALLOW")
            ),
            "reasons": sorted(plan_blocker_ids) or (["missing_execution_plan"] if require_plan and not plan_result else []),
        },
        {
            "role": "operator",
            "vote": action_result.get("decision", "REVIEW"),
            "reasons": sorted(action_blockers or action_reviews),
        },
        {
            "role": "payout_verifier",
            "vote": "REVIEW" if public_or_claim_action and not (payout_route or "").strip() else "ALLOW",
            "reasons": ["missing_verified_payout_route"] if public_or_claim_action and not (payout_route or "").strip() else [],
        },
    ]
    hard_blocks = [
        vote["role"]
        for vote in votes
        if vote["vote"] == "BLOCK"
        or "opportunity_blocked" in vote.get("reasons", [])
        or any(str(reason).endswith("_forbidden") for reason in vote.get("reasons", []))
    ]
    reviews = [vote["role"] for vote in votes if vote["vote"] == "REVIEW"]
    return {
        "version": ROLE_QUORUM_VERSION,
        "votes": votes,
        "hard_block_roles": hard_blocks,
        "review_roles": reviews,
        "untrusted_text_raw_copy_stored": False,
        "minimum_clearance": "No BLOCK votes; REVIEW votes need explicit scoped rationale before execution.",
    }


def build_record(
    *,
    name: str,
    source_url: str | None,
    reward: str | None,
    opportunity_text: str,
    execution_plan: str,
    review_rationale: str | None,
    require_plan: bool,
    policy: dict[str, Any],
    actions: list[str] | None = None,
    payout_route: str | None = None,
    explicit_user_approval: bool = False,
) -> dict[str, Any]:
    opportunity_result = evaluate(opportunity_text, policy)
    plan_result = evaluate(execution_plan, policy) if execution_plan.strip() else None
    action_result = evaluate_actions(
        actions,
        payout_route=payout_route,
        explicit_user_approval=explicit_user_approval,
    )
    quorum = role_quorum(
        opportunity_result,
        plan_result,
        action_result,
        payout_route=payout_route,
        require_plan=require_plan,
    )
    decision, decision_reasons = combine_decision(
        opportunity_result,
        plan_result,
        action_result,
        require_plan,
    )
    may_execute = decision == "ALLOW" or (decision == "REVIEW" and bool(review_rationale))

    opportunity_signals = scan_signal_ids(opportunity_text)
    plan_signals = scan_signal_ids(execution_plan) if execution_plan.strip() else []
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")

    return {
        "id": stable_id(name, source_url, opportunity_text, execution_plan),
        "timestamp_utc": now,
        "pipeline_version": PIPELINE_VERSION,
        "name": name,
        "source_url": source_url,
        "reward": reward,
        "decision": decision,
        "decision_reasons": decision_reasons,
        "may_execute": may_execute,
        "review_rationale": review_rationale,
        "roles": {
            "scout": {
                "opportunity_sha256": sha256_text(opportunity_text),
                "source_urls": extract_urls("\n".join([source_url or "", opportunity_text])),
                "risk_signals": opportunity_signals,
                "risk_score": risk_score(opportunity_signals, opportunity_result),
            },
            "adversary": {
                "prompt_injection_signal_ids": [
                    item["id"]
                    for item in opportunity_result.get("blockers", [])
                    if item["id"]
                    in {
                        "prompt_injection_ignore_rules",
                        "instruction_exfiltration",
                        "encoded_instruction_or_secret_exfiltration",
                        "secret_exfiltration",
                    }
                ],
                "treat_external_text_as_untrusted": True,
            },
            "safety": {
                "opportunity_gate": summarize_gate(opportunity_result),
                "hard_blockers_are_final": True,
            },
            "builder": {
                "execution_plan_required": require_plan,
                "execution_plan_present": bool(execution_plan.strip()),
                "execution_plan_sha256": sha256_text(execution_plan) if execution_plan.strip() else None,
                "execution_plan_signals": plan_signals,
                "execution_plan_gate": summarize_gate(plan_result) if plan_result else None,
                "must_not_use_user_socials": True,
                "must_not_exfiltrate_internal_context": True,
                "must_not_spend_or_sign_without_explicit_user_approval": True,
            },
            "operator": {
                "action_gate": action_result,
                "payout_route_sha256": sha256_text(payout_route) if (payout_route or "").strip() else None,
            },
            "quorum": quorum,
        },
    }


def write_audit(record: dict[str, Any]) -> Path:
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    day = datetime.now(timezone.utc).strftime("%Y%m%d")
    path = AUDIT_DIR / f"protective_{day}.jsonl"
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, sort_keys=True) + "\n")
    return path


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Scout -> Safety -> Builder preflight.")
    parser.add_argument("--name", required=True, help="Human-readable opportunity name.")
    parser.add_argument("--source-url", help="Canonical issue/gig/bounty URL.")
    parser.add_argument("--reward", help="Advertised reward, if known.")
    parser.add_argument("--file", help="Opportunity description file.")
    parser.add_argument("--text", help="Opportunity description text.")
    parser.add_argument("--execution-plan", help="Short plan for the first write/submit/public action.")
    parser.add_argument("--execution-plan-file", help="Read execution plan from a file.")
    parser.add_argument(
        "--action",
        action="append",
        help=(
            "Planned action type. Repeat as needed. Known actions include discover, clone, "
            "local_edit, public_pr, public_submission, claim, account_create, external_login, "
            "install, wallet_link, wallet_sign, payment_setup, spend, kyc, user_social."
        ),
    )
    parser.add_argument(
        "--payout-route",
        help="Brief verified payout route, stored only as a hash in the audit record.",
    )
    parser.add_argument(
        "--explicit-user-approval",
        action="store_true",
        help="Specific approval for wallet signing or spending. Broad standing permission is not enough.",
    )
    parser.add_argument(
        "--review-rationale",
        help="Required to execute when either opportunity text or plan returns REVIEW.",
    )
    parser.add_argument(
        "--no-require-plan",
        action="store_true",
        help="Allow discovery-only triage without a Builder plan.",
    )
    parser.add_argument("--policy", default=str(DEFAULT_POLICY), help="Policy JSON path.")
    parser.add_argument("--json", action="store_true", help="Print JSON output.")
    args = parser.parse_args()

    opportunity_text = read_text(args.text, args.file)
    execution_plan = read_text(args.execution_plan, args.execution_plan_file)
    if not opportunity_text.strip():
        print("No opportunity text provided.", file=sys.stderr)
        return 1

    policy = json.loads(Path(args.policy).read_text(encoding="utf-8"))
    record = build_record(
        name=args.name,
        source_url=args.source_url,
        reward=args.reward,
        opportunity_text=opportunity_text,
        execution_plan=execution_plan,
        review_rationale=args.review_rationale,
        require_plan=not args.no_require_plan,
        actions=args.action,
        payout_route=args.payout_route,
        explicit_user_approval=args.explicit_user_approval,
        policy=policy,
    )
    audit_path = write_audit(record)

    output = {**record, "audit_path": str(audit_path)}
    if args.json:
        print(json.dumps(output, indent=2, sort_keys=True))
    else:
        print(f"Opportunity: {args.name}")
        print(f"ID: {record['id']}")
        print(f"Decision: {record['decision']}")
        print(f"May execute: {'yes' if record['may_execute'] else 'no'}")
        if record["decision_reasons"]:
            print(f"Reasons: {', '.join(record['decision_reasons'])}")
        print(f"Audit: {audit_path}")

    if record["decision"] == "BLOCK":
        return 3
    if record["decision"] == "REVIEW" and not record["review_rationale"]:
        return 2
    if not record["may_execute"]:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

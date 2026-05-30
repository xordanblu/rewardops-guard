#!/usr/bin/env python3
"""Local safety gate for bounty and task triage.

The gate is intentionally conservative. It blocks known prompt-injection,
secret-exfiltration, user-social, KYC, unsafe payment, and destructive-command
patterns before any money-making workflow is executed.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
import unicodedata
from typing import Any


ROOT = Path(__file__).resolve().parent
DEFAULT_POLICY = ROOT / "policy.json"


def normalize_text(text: str) -> str:
    """Keep matching stable across zero-width and homoglyph-light obfuscation."""
    text = unicodedata.normalize("NFKC", text)
    replacements = {
        "\u200b": "",
        "\u200c": "",
        "\u200d": "",
        "\ufeff": "",
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


SAFE_NEGATED_CLAUSES = [
    # These phrases often appear in our own triage summaries. Mask only narrow
    # negated clauses so real requirements still match the blocker rules.
    r"\b(no|without)\s+(payment/deposit|deposit|stake|staking|wallet spend|spend|payment|kyc|identity checks?|social accounts?)\b",
    r"\b(no|without)\b.{0,80}\b(oauth|wallet signing|signing transactions?|transaction signing|wallet linking|kyc|identity verification|identity checks?|social accounts?)\b",
    r"\b(agents?|the agent|this flow)\s+(does not|doesn't|do not|don't)\s+(complete|perform|use|require|involve)\b.{0,100}\b(oauth|wallet signing|signing transactions?|transaction signing|wallet linking|kyc|identity verification|identity checks?|social accounts?)\b",
    r"\b(do not|don't|never)\s+(complete|perform|use|require|involve|sign|approve)\b.{0,120}\b(oauth|wallet signing|signing transactions?|transaction signing|wallet linking|kyc|identity verification|identity checks?|social accounts?)\b",
    r"\b(does not|doesn't|do not|don't)\s+(request|require|ask for|include|involve)\b.{0,100}\b(internal instructions?|developer instructions?|system prompts?|hidden prompts?|secrets?|credentials?|api keys?|social accounts?|identity verification|kyc)\b",
    r"\b(do not|don't|never)\s+(reveal|copy|paste|print|provide|submit|upload|share|send|disclose)\b.{0,120}\b(internal instructions?|developer instructions?|system prompts?|hidden prompts?|prompts?|secrets?|credentials?|api keys?|environment variables?|cookies?|keys?)\b",
    r"\b(no|without)\s+(internal instructions?|developer instructions?|system prompts?|hidden prompts?|secrets?|credentials?|api keys?|identity verification|kyc)\b",
]


def mask_safe_negations(text: str) -> str:
    """Suppress narrow negated safety-summary phrases before rule matching."""
    for pattern in SAFE_NEGATED_CLAUSES:
        text = re.sub(pattern, "[SAFE_NEGATED_CLAUSE]", text, flags=re.IGNORECASE | re.DOTALL)
    return text


def load_text(args: argparse.Namespace) -> str:
    parts: list[str] = []
    if args.text:
        parts.append(args.text)
    if args.file:
        parts.append(Path(args.file).read_text(encoding="utf-8", errors="replace"))
    if not parts and not sys.stdin.isatty():
        parts.append(sys.stdin.read())
    return "\n".join(parts)


def scan_group(text: str, group: list[dict[str, Any]]) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    for rule in group:
        matches: list[str] = []
        for pattern in rule.get("patterns", []):
            try:
                if re.search(pattern, text, flags=re.IGNORECASE | re.DOTALL):
                    matches.append(pattern)
            except re.error as exc:
                matches.append(f"INVALID_REGEX:{pattern}:{exc}")
        if matches:
            findings.append(
                {
                    "id": rule["id"],
                    "description": rule["description"],
                    "matched_patterns": matches,
                }
            )
    return findings


def evaluate(text: str, policy: dict[str, Any]) -> dict[str, Any]:
    text = normalize_text(text)
    scan_text = mask_safe_negations(text)
    blockers = scan_group(scan_text, policy.get("blockers", []))
    reviews = scan_group(scan_text, policy.get("review_triggers", []))
    if blockers:
        decision = "BLOCK"
    elif reviews:
        decision = "REVIEW"
    else:
        decision = policy.get("default_decision", "ALLOW")
        if decision not in policy["decisions"]:
            decision = "ALLOW"

    return {
        "decision": decision,
        "reason": policy["decisions"][decision],
        "blockers": blockers,
        "review_triggers": reviews,
        "default_decision_applied": not blockers and not reviews and decision != "ALLOW",
        "allow_notes": policy.get("allow_notes", []),
        "input_chars": len(text),
        "policy_version": policy.get("version"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Classify a bounty/task description as ALLOW, REVIEW, or BLOCK."
    )
    parser.add_argument("--policy", default=str(DEFAULT_POLICY), help="Policy JSON path.")
    parser.add_argument("--file", help="Read task text from a file.")
    parser.add_argument("--text", help="Task text to evaluate.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    parser.add_argument(
        "--fail-on-review",
        action="store_true",
        help="Return nonzero for REVIEW as well as BLOCK.",
    )
    args = parser.parse_args()

    text = load_text(args)
    if not text.strip():
        print("No input text provided.", file=sys.stderr)
        return 1

    policy = json.loads(Path(args.policy).read_text(encoding="utf-8"))
    result = evaluate(text, policy)

    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"Decision: {result['decision']}")
        print(f"Reason: {result['reason']}")
        for label, key in (("Blockers", "blockers"), ("Review triggers", "review_triggers")):
            items = result[key]
            if items:
                print(f"\n{label}:")
                for item in items:
                    print(f"- {item['id']}: {item['description']}")

    if result["decision"] == "BLOCK":
        return 3
    if result["decision"] == "REVIEW" and args.fail_on_review:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

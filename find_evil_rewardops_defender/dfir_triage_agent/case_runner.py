#!/usr/bin/env python3
"""Ground-truth runner for the FIND EVIL local case."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any

try:
    from dfir_triage_agent import rewardops_defender
except ModuleNotFoundError:  # pragma: no cover - direct script execution fallback
    import rewardops_defender  # type: ignore


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CASE = ROOT / "cases" / "find_evil_local_case.json"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def one_line(value: Any, limit: int = 180) -> str:
    return " ".join(str(value or "").split())[:limit]


def load_case(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("case file must contain a JSON object")
    if not isinstance(payload.get("events"), list):
        raise ValueError("case file must contain an events array")
    return payload


def event_id_map(events: list[dict[str, Any]]) -> dict[str, str]:
    mapping: dict[str, str] = {}
    for event in events:
        case_event_id = str(event.get("case_event_id") or "")
        if not case_event_id:
            continue
        sanitized = rewardops_defender.sanitize_event(event)
        mapping[sanitized["event_id"]] = case_event_id
    return mapping


def score_report(case: dict[str, Any], defender_report: dict[str, Any]) -> dict[str, Any]:
    ground_truth = case.get("ground_truth") or {}
    labels = ground_truth.get("event_labels") or {}
    expected_hypotheses = set(ground_truth.get("expected_hypotheses") or [])
    case_ids_by_event_id = event_id_map(case["events"])

    false_positive_events: list[str] = []
    false_negative_events: list[str] = []
    signal_misses: list[dict[str, Any]] = []
    detected_malicious = 0
    expected_malicious = 0
    true_negative_adjustments = 0

    for event in defender_report.get("timeline") or []:
        case_event_id = case_ids_by_event_id.get(event.get("event_id"), "")
        expected = labels.get(case_event_id, {})
        expected_signals = set(expected.get("expected_signals") or [])
        actual_signals = set(event.get("signals") or [])
        malicious = bool(expected.get("malicious"))
        detected = bool(actual_signals) and not bool(event.get("benign_context_adjustment"))

        if malicious:
            expected_malicious += 1
            if detected:
                detected_malicious += 1
            else:
                false_negative_events.append(case_event_id)
        elif detected and event.get("severity") in {"medium", "high", "critical"}:
            false_positive_events.append(case_event_id)

        if expected.get("expected_adjustment") and event.get("benign_context_adjustment"):
            true_negative_adjustments += 1

        missing = sorted(expected_signals - actual_signals)
        if missing:
            signal_misses.append({"case_event_id": case_event_id, "missing": missing})

    actual_hypotheses = {item.get("id") for item in defender_report.get("hypotheses") or []}
    hypothesis_misses = sorted(expected_hypotheses - actual_hypotheses)
    false_positive_count = len(false_positive_events)
    recall = detected_malicious / expected_malicious if expected_malicious else 1.0
    precision_denominator = detected_malicious + false_positive_count
    precision = detected_malicious / precision_denominator if precision_denominator else 1.0

    return {
        "expected_malicious_events": expected_malicious,
        "detected_malicious_events": detected_malicious,
        "false_positive_events": false_positive_events,
        "false_negative_events": false_negative_events,
        "true_negative_adjustments": true_negative_adjustments,
        "signal_misses": signal_misses,
        "hypothesis_misses": hypothesis_misses,
        "event_precision": round(precision, 4),
        "event_recall": round(recall, 4),
        "passes_ground_truth": not false_positive_events
        and not false_negative_events
        and not signal_misses
        and not hypothesis_misses,
    }


def build_case_report(case: dict[str, Any]) -> dict[str, Any]:
    defender_report = rewardops_defender.build_report(case["events"], case_id=case.get("case_id") or "find-evil-local-case")
    score = score_report(case, defender_report)
    return {
        "schema": "rewardops.case_score.v1",
        "generated_at": now_iso(),
        "case_id": one_line(case.get("case_id"), 80),
        "case_name": one_line(case.get("name"), 180),
        "case_source": one_line(case.get("source"), 260),
        "defender_verdict": defender_report.get("verdict"),
        "event_count": defender_report.get("event_count"),
        "high_event_count": defender_report.get("high_event_count"),
        "self_correction_count": len(defender_report.get("self_corrections") or []),
        "score": score,
        "defender_report": defender_report,
    }


def write_markdown(path: Path, report: dict[str, Any]) -> None:
    score = report["score"]
    lines = [
        "# FIND EVIL Local Case Ground Truth Report",
        "",
        f"Generated: {report['generated_at']}",
        f"Case: {report['case_id']} - {report['case_name']}",
        f"Source: {report['case_source']}",
        f"Verdict: {report['defender_verdict']}",
        "",
        "## Score",
        "",
        f"- Expected malicious events: {score['expected_malicious_events']}",
        f"- Detected malicious events: {score['detected_malicious_events']}",
        f"- False positives: {len(score['false_positive_events'])}",
        f"- False negatives: {len(score['false_negative_events'])}",
        f"- Event precision: {score['event_precision']:.4f}",
        f"- Event recall: {score['event_recall']:.4f}",
        f"- True negative/self-corrected benign adjustments: {score['true_negative_adjustments']}",
        f"- Passes ground truth: {score['passes_ground_truth']}",
        "",
        "## Evidence Boundary",
        "",
        "- The case is synthetic and contains no real secrets, credentials, wallet keys, or internal instructions.",
        "- Public reports cite event ids, hashes, timestamps, sources, classifications, and scores.",
        "- Raw hostile event text is not copied into the generated defender timeline.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Run RewardOps Defender against a labelled FIND EVIL local case.")
    p.add_argument("--case-json", type=Path, default=DEFAULT_CASE)
    p.add_argument("--json-output", type=Path, required=True)
    p.add_argument("--markdown-output", type=Path, required=True)
    return p


def main() -> int:
    args = parser().parse_args()
    report = build_case_report(load_case(args.case_json))
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown(args.markdown_output, report)
    print(
        json.dumps(
            {
                "case_id": report["case_id"],
                "passes_ground_truth": report["score"]["passes_ground_truth"],
                "event_precision": report["score"]["event_precision"],
                "event_recall": report["score"]["event_recall"],
            }
        )
    )
    return 0 if report["score"]["passes_ground_truth"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

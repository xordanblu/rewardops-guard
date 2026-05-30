#!/usr/bin/env python3
"""Build a local InterSystems AI Agents for FHIR submission-readiness packet."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
KIT_ROOT = Path(__file__).resolve().parent

CONTEST_SOURCE_URL = "https://community.intersystems.com/post/intersystems-programming-contest-ai-agents-fhir"
TECH_BONUS_SOURCE_URL = "https://community.intersystems.com/post/technology-bonuses-intersystems-programming-contest-ai-agents-fhir"
OPEN_EXCHANGE_URL = "https://openexchange.intersystems.com/contests?archive=1"

LOCAL_ARTIFACTS = [
    "rewardops_guard/delivery_kits/intersystems_fhir_agent_pack/README.md",
    "rewardops_guard/delivery_kits/intersystems_fhir_agent_pack/SUBMISSION_DRAFT.md",
    "rewardops_guard/delivery_kits/intersystems_fhir_agent_pack/ARTICLE_DRAFT.md",
    "rewardops_guard/delivery_kits/intersystems_fhir_agent_pack/Dockerfile",
    "rewardops_guard/delivery_kits/intersystems_fhir_agent_pack/docker-compose.yml",
    "rewardops_guard/delivery_kits/intersystems_fhir_agent_pack/module.xml",
    "rewardops_guard/delivery_kits/intersystems_fhir_agent_pack/fhir_summary_agent.py",
    "rewardops_guard/delivery_kits/intersystems_fhir_agent_pack/demo_server.py",
    "rewardops_guard/delivery_kits/intersystems_fhir_agent_pack/contest_preflight.py",
    "rewardops_guard/delivery_kits/intersystems_fhir_agent_pack/sample_patient_bundle.json",
    "rewardops_guard/delivery_kits/intersystems_fhir_agent_pack/sample_summary_ed_doctor.json",
    "rewardops_guard/delivery_kits/intersystems_fhir_agent_pack/sample_summary_ed_doctor.md",
    "rewardops_guard/delivery_kits/intersystems_fhir_agent_pack/src/cls/RewardOps/FHIR/CareBriefAgent.cls",
    "rewardops_guard/delivery_kits/intersystems_fhir_agent_pack/test_fhir_summary_agent.py",
]

APPROVAL_GATES = [
    "InterSystems Developer Community / Open Exchange account creation or login",
    "Public GitHub/GitLab repository publication",
    "Demo video recording or upload",
    "Open Exchange contest submission",
    "Identity verification for cash prize collection",
    "Real patient data, PHI, credentials, cloud deployment, paid API spend, wallet action, or social posting",
]

SUGGESTED_TRACKS = [
    "Smart Patient Summary Generator",
    "Medication Safety and Interaction Assistant",
    "AI-Powered Care Plan Navigator",
]


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def file_status(path: str) -> dict[str, Any]:
    full = ROOT / path
    return {
        "path": path,
        "exists": full.exists(),
        "size_bytes": full.stat().st_size if full.exists() and full.is_file() else 0,
    }


def build_packet() -> dict[str, Any]:
    artifacts = [file_status(path) for path in LOCAL_ARTIFACTS]
    missing = [item["path"] for item in artifacts if not item["exists"]]
    return {
        "generated_at": now_iso(),
        "kit": "intersystems_fhir_agent_pack",
        "source_urls": [CONTEST_SOURCE_URL, TECH_BONUS_SOURCE_URL, OPEN_EXCHANGE_URL],
        "prize_context": {
            "total_pool_usd": 12000,
            "expert_first_place_usd": 5000,
            "expert_second_place_usd": 2500,
            "expert_third_place_usd": 1000,
            "community_first_place_usd": 1000,
            "submission_deadline": "2026-06-07 23:59 EST",
            "voting_period": "2026-06-08 through 2026-06-14 23:59 EST",
        },
        "bonus_context": {
            "suggested_task": 5,
            "intersystems_fhir_server_usage": 2,
            "vector_search_usage": 4,
            "embedded_python": 3,
            "llm_or_langchain_usage": 3,
            "docker_container_usage": 2,
            "zpm_package_deployment": 2,
            "online_demo": 2,
            "first_time_contribution": 3,
            "youtube_video": 3,
        },
        "project": {
            "name": "FHIR Care Brief Agent",
            "one_liner": "A synthetic-data-first FHIR agent that turns local or read-only server FHIR resources into role-specific care summaries.",
            "contest_fit": "Matches the Smart Patient Summary Generator bonus idea and now includes medication-safety, care-plan navigator, read-only FHIR REST fetching, Docker, ZPM/IPM packaging, local web demo, and submission/article drafts for a stronger expert-judging story.",
            "suggested_tracks": SUGGESTED_TRACKS,
            "agent_workflow": [
                "Load an approved FHIR Bundle or fetch a patient-centered Bundle from an approved read-only FHIR REST base URL.",
                "Extract active clinical signals from the required resources.",
                "Generate current issues, recent changes, and risks/follow-up items.",
                "Generate medication-safety findings, care-plan task candidates, and evidence traceability.",
                "Render role-specific outputs for ED doctor, care manager, patient, or family caregiver.",
                "Ship Docker, docker-compose, module.xml, and a minimal RewardOps.FHIR ObjectScript bridge class for IRIS/Open Exchange packaging review.",
                "Expose a dependency-free local web demo with HTML dashboard and /summary.json endpoint.",
                "Prepare Open Exchange submission and Developer Community article drafts without publishing them.",
                "Block PHI, account, publication, video, KYC, spend, wallet, and social steps until approved.",
            ],
        },
        "local_artifacts": artifacts,
        "missing_local_artifacts": missing,
        "ready_locally": not missing,
        "approval_gates_before_public_submission": APPROVAL_GATES,
        "side_effects": "none; packet generation is local only",
    }


def write_markdown(packet: dict[str, Any], output: Path) -> None:
    lines = [
        "# InterSystems FHIR Agent Packet",
        "",
        f"Generated: {packet['generated_at']}",
        f"Project: {packet['project']['name']}",
        f"Expert first-place fit: ${packet['prize_context']['expert_first_place_usd']:.0f}",
        f"Submission deadline: {packet['prize_context']['submission_deadline']}",
        "",
        "## Angle",
        "",
        packet["project"]["one_liner"],
        "",
        packet["project"]["contest_fit"],
        "",
        "## Agent Workflow",
        "",
    ]
    lines.extend(f"- {step}" for step in packet["project"]["agent_workflow"])
    lines.extend(["", "## Suggested Contest Ideas Covered", ""])
    lines.extend(f"- {item}" for item in packet["project"]["suggested_tracks"])
    lines.extend(["", "## Local Artifacts", ""])
    for item in packet["local_artifacts"]:
        status = "ready" if item["exists"] else "missing"
        lines.append(f"- {status}: `{item['path']}`")
    lines.extend(["", "## Approval Gates", ""])
    lines.extend(f"- {gate}" for gate in packet["approval_gates_before_public_submission"])
    lines.extend(["", "## Sources", ""])
    lines.extend(f"- {url}" for url in packet["source_urls"])
    lines.extend(["", f"Local ready: `{str(packet['ready_locally']).lower()}`"])
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json-output", type=Path, default=KIT_ROOT / "contest_packet.json")
    parser.add_argument("--markdown-output", type=Path, default=KIT_ROOT / "contest_packet.md")
    args = parser.parse_args()

    packet = build_packet()
    args.json_output.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown(packet, args.markdown_output)
    print(json.dumps({"json": str(args.json_output), "markdown": str(args.markdown_output), "ready_locally": packet["ready_locally"]}))
    return 0 if packet["ready_locally"] else 2


if __name__ == "__main__":
    raise SystemExit(main())

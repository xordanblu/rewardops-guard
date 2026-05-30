#!/usr/bin/env python3
"""Local preflight for the InterSystems FHIR contest route.

This script validates local artifacts only. It deliberately reports external
submission gates instead of creating accounts, publishing repos, uploading
videos, submitting to Open Exchange, handling PHI, or verifying identity.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
from typing import Any
from xml.etree import ElementTree

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from rewardops_guard.delivery_kits.intersystems_fhir_agent_pack.fhir_summary_agent import (
    REQUIRED_CONTEST_RESOURCES,
    ROLE_GUIDANCE,
    load_bundle,
    render_markdown,
    summarize_bundle,
)


ROOT = Path(__file__).resolve().parents[3]
KIT_ROOT = Path(__file__).resolve().parent

REQUIRED_LOCAL_FILES = [
    "README.md",
    "SUBMISSION_DRAFT.md",
    "ARTICLE_DRAFT.md",
    "Dockerfile",
    "docker-compose.yml",
    "module.xml",
    "fhir_summary_agent.py",
    "demo_server.py",
    "sample_patient_bundle.json",
    "test_fhir_summary_agent.py",
    "contest_packet.py",
    "src/cls/RewardOps/FHIR/CareBriefAgent.cls",
]

EXTERNAL_BLOCKERS = [
    "Create or log into InterSystems Developer Community / Open Exchange account",
    "Publish the app as an open-source GitHub or GitLab repository",
    "Publish the app on InterSystems Open Exchange",
    "Apply the Open Exchange app to the contest before 2026-06-07 23:59 EST",
    "Provide prize identity information if InterSystems requests it",
    "Approve any public video/article/demo publication",
]


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def bundle_resource_types(bundle: dict[str, Any]) -> set[str]:
    resource_types = set()
    for entry in bundle.get("entry", []):
        resource = entry.get("resource") if isinstance(entry, dict) else None
        if isinstance(resource, dict) and resource.get("resourceType"):
            resource_types.add(str(resource["resourceType"]))
    return resource_types


def local_file_checks() -> list[dict[str, Any]]:
    checks = []
    for name in REQUIRED_LOCAL_FILES:
        path = KIT_ROOT / name
        checks.append({"path": name, "exists": path.exists(), "size_bytes": path.stat().st_size if path.exists() else 0})
    return checks


def packaging_checks() -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    dockerfile = KIT_ROOT / "Dockerfile"
    docker_compose = KIT_ROOT / "docker-compose.yml"
    module_xml = KIT_ROOT / "module.xml"
    cls_file = KIT_ROOT / "src/cls/RewardOps/FHIR/CareBriefAgent.cls"

    dockerfile_text = dockerfile.read_text(encoding="utf-8") if dockerfile.exists() else ""
    checks.append(
        {
            "name": "iris_health_container_image",
            "ok": "intersystemsdc/irishealth-community:latest" in dockerfile_text,
            "evidence": "Dockerfile references InterSystems IRIS for Health Community image",
        }
    )
    checks.append(
        {
            "name": "docker_build_smoke_command",
            "ok": "fhir_summary_agent.py" in dockerfile_text and "--role ed_doctor" in dockerfile_text,
            "evidence": "Dockerfile runs the synthetic FHIR summary agent during image build",
        }
    )

    compose_text = docker_compose.read_text(encoding="utf-8") if docker_compose.exists() else ""
    checks.append(
        {
            "name": "docker_compose_service",
            "ok": "fhir-care-brief-agent" in compose_text and "52773:52773" in compose_text,
            "evidence": "docker-compose.yml exposes the standard local IRIS web port",
        }
    )

    try:
        tree = ElementTree.parse(module_xml)
        root = tree.getroot()
        module_text = " ".join(element.text or "" for element in root.iter())
        resource_names = [element.attrib.get("Name", "") for element in root.iter() if element.tag == "Resource"]
        csp_urls = [element.attrib.get("Url", "") for element in root.iter() if element.tag == "CSPApplication"]
        module_ok = "fhir-care-brief-agent" in module_text
        resource_ok = "RewardOps.FHIR.PKG" in resource_names
        csp_ok = "/fhir-care-brief-agent" in csp_urls
    except (ElementTree.ParseError, OSError):
        module_ok = False
        resource_ok = False
        csp_ok = False
    checks.extend(
        [
            {"name": "zpm_module_name", "ok": module_ok, "evidence": "module.xml declares fhir-care-brief-agent"},
            {"name": "zpm_resource_package", "ok": resource_ok, "evidence": "module.xml packages RewardOps.FHIR classes"},
            {"name": "zpm_csp_application", "ok": csp_ok, "evidence": "module.xml declares /fhir-care-brief-agent web app"},
        ]
    )

    cls_text = cls_file.read_text(encoding="utf-8") if cls_file.exists() else ""
    checks.append(
        {
            "name": "objectscript_bridge_class",
            "ok": "Class RewardOps.FHIR.CareBriefAgent" in cls_text and "SummaryRoles" in cls_text,
            "evidence": "ObjectScript package bridge class is present",
        }
    )
    submission_draft = (KIT_ROOT / "SUBMISSION_DRAFT.md").read_text(encoding="utf-8") if (KIT_ROOT / "SUBMISSION_DRAFT.md").exists() else ""
    article_draft = (KIT_ROOT / "ARTICLE_DRAFT.md").read_text(encoding="utf-8") if (KIT_ROOT / "ARTICLE_DRAFT.md").exists() else ""
    checks.append(
        {
            "name": "open_exchange_submission_draft",
            "ok": "Application Name" in submission_draft and "FHIR Care Brief Agent" in submission_draft,
            "evidence": "Open Exchange submission draft is present but not submitted",
        }
    )
    checks.append(
        {
            "name": "developer_community_article_draft",
            "ok": "Synthetic-Data-First" in article_draft and "FHIR Server Path" in article_draft,
            "evidence": "Developer Community article draft is present but not published",
        }
    )
    demo_server = (KIT_ROOT / "demo_server.py").read_text(encoding="utf-8") if (KIT_ROOT / "demo_server.py").exists() else ""
    checks.append(
        {
            "name": "local_web_demo",
            "ok": "ThreadingHTTPServer" in demo_server and "summary.json" in demo_server,
            "evidence": "Dependency-free local web demo with JSON endpoint is present",
        }
    )
    return checks


def role_checks(bundle: dict[str, Any]) -> list[dict[str, Any]]:
    checks = []
    for role in sorted(ROLE_GUIDANCE):
        summary = summarize_bundle(bundle, role)
        markdown = render_markdown(summary)
        checks.append(
            {
                "role": role,
                "ok": all(
                    [
                        bool(summary.current_issues),
                        bool(summary.recent_changes),
                        bool(summary.risks_follow_up),
                        bool(summary.medication_safety),
                        bool(summary.care_plan_next_steps),
                        "## Evidence Trace" in markdown,
                    ]
                ),
                "sections": {
                    "current_issues": len(summary.current_issues),
                    "recent_changes": len(summary.recent_changes),
                    "risks_follow_up": len(summary.risks_follow_up),
                    "medication_safety": len(summary.medication_safety),
                    "care_plan_next_steps": len(summary.care_plan_next_steps),
                    "evidence_trace": len(summary.evidence_trace),
                },
            }
        )
    return checks


def build_report() -> dict[str, Any]:
    bundle = load_bundle()
    resource_types = bundle_resource_types(bundle)
    missing_resources = sorted(REQUIRED_CONTEST_RESOURCES - resource_types)
    files = local_file_checks()
    roles = role_checks(bundle)
    packaging = packaging_checks()
    local_ok = (
        all(item["exists"] and item["size_bytes"] > 0 for item in files)
        and not missing_resources
        and all(item["ok"] for item in roles)
        and all(item["ok"] for item in packaging)
    )
    return {
        "checked_at": now_iso(),
        "kit": "intersystems_fhir_agent_pack",
        "local_ok": local_ok,
        "external_submission_ok": False,
        "contest_value": {
            "expert_first_place_usd": 5000,
            "total_prize_pool_usd": 12000,
            "submission_deadline": "2026-06-07 23:59 EST",
        },
        "local_file_checks": files,
        "resource_coverage": {
            "required": sorted(REQUIRED_CONTEST_RESOURCES),
            "found": sorted(resource_types),
            "missing": missing_resources,
        },
        "role_checks": roles,
        "packaging_checks": packaging,
        "covered_bonus_angles": [
            "Suggested task: Smart Patient Summary Generator",
            "InterSystems FHIR Server container scaffold",
            "Embedded Python-style local agent logic",
            "LLM/AI-agent-ready summary workflow",
            "Read-only FHIR REST fetch path for approved test servers",
            "Docker container scaffold",
            "ZPM/IPM module.xml package scaffold",
            "Open Exchange submission and Developer Community article drafts",
            "Dependency-free local web demo for judge review",
            "Open Exchange gates documented but not executed",
        ],
        "external_blockers_before_contest_submission": EXTERNAL_BLOCKERS,
        "side_effects": "none; local read/validation only",
    }


def write_markdown(report: dict[str, Any], path: Path) -> None:
    lines = [
        "# InterSystems FHIR Contest Preflight",
        "",
        f"Checked: {report['checked_at']}",
        f"Local OK: `{str(report['local_ok']).lower()}`",
        f"External submission OK: `{str(report['external_submission_ok']).lower()}`",
        f"First-place target: `${report['contest_value']['expert_first_place_usd']}`",
        f"Deadline: {report['contest_value']['submission_deadline']}",
        "",
        "## Resource Coverage",
        "",
    ]
    for resource_type in report["resource_coverage"]["required"]:
        status = "present" if resource_type in report["resource_coverage"]["found"] else "missing"
        lines.append(f"- {status}: {resource_type}")
    lines.extend(["", "## Role Checks", ""])
    for role in report["role_checks"]:
        lines.append(f"- {'ok' if role['ok'] else 'missing'}: {role['role']}")
    lines.extend(["", "## Packaging Checks", ""])
    for check in report["packaging_checks"]:
        lines.append(f"- {'ok' if check['ok'] else 'missing'}: {check['name']} - {check['evidence']}")
    lines.extend(["", "## External Blockers", ""])
    lines.extend(f"- {item}" for item in report["external_blockers_before_contest_submission"])
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json-output", type=Path, default=KIT_ROOT / "contest_preflight.json")
    parser.add_argument("--markdown-output", type=Path, default=KIT_ROOT / "contest_preflight.md")
    args = parser.parse_args()

    report = build_report()
    args.json_output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown(report, args.markdown_output)
    print(json.dumps({"json": str(args.json_output), "markdown": str(args.markdown_output), "local_ok": report["local_ok"]}))
    return 0 if report["local_ok"] else 2


if __name__ == "__main__":
    raise SystemExit(main())

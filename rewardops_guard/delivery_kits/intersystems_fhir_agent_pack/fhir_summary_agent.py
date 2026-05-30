#!/usr/bin/env python3
"""Local FHIR summary agent for the InterSystems contest route.

This module works on synthetic or approved FHIR Bundles only. It does not call
InterSystems APIs, submit contest entries, store PHI, or create accounts.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any, Iterable


KIT_ROOT = Path(__file__).resolve().parent
SAMPLE_BUNDLE = KIT_ROOT / "sample_patient_bundle.json"


ROLE_GUIDANCE = {
    "ed_doctor": {
        "label": "ED doctor",
        "focus": "acute risk, abnormal recent data, allergies, and immediate follow-up",
    },
    "care_manager": {
        "label": "Care manager",
        "focus": "care gaps, active plan tasks, adherence questions, and coordination",
    },
    "patient": {
        "label": "Patient",
        "focus": "plain-language explanation and questions to ask the care team",
    },
    "family_caregiver": {
        "label": "Family caregiver",
        "focus": "plain-language next steps, warning signs, and care-team questions",
    },
}

REQUIRED_CONTEST_RESOURCES = {
    "Patient",
    "Condition",
    "MedicationRequest",
    "AllergyIntolerance",
    "Observation",
    "Encounter",
    "CarePlan",
}


@dataclass(frozen=True)
class FhirSummary:
    patient_label: str
    role: str
    current_issues: list[str]
    recent_changes: list[str]
    risks_follow_up: list[str]
    medication_safety: list[str]
    care_plan_next_steps: list[str]
    evidence_trace: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "patient_label": self.patient_label,
            "role": self.role,
            "current_issues": self.current_issues,
            "recent_changes": self.recent_changes,
            "risks_follow_up": self.risks_follow_up,
            "medication_safety": self.medication_safety,
            "care_plan_next_steps": self.care_plan_next_steps,
            "evidence_trace": self.evidence_trace,
        }


def load_bundle(path: Path = SAMPLE_BUNDLE) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        bundle = json.load(handle)
    if bundle.get("resourceType") != "Bundle":
        raise ValueError("Expected a FHIR Bundle resource")
    return bundle


def iter_resources(bundle: dict[str, Any], resource_type: str | None = None) -> Iterable[dict[str, Any]]:
    for entry in bundle.get("entry", []):
        resource = entry.get("resource") if isinstance(entry, dict) else None
        if not isinstance(resource, dict):
            continue
        if resource_type is None or resource.get("resourceType") == resource_type:
            yield resource


def text_at(resource: dict[str, Any], *keys: str) -> str:
    value: Any = resource
    for key in keys:
        if isinstance(value, dict):
            value = value.get(key)
        else:
            return ""
    return str(value or "").strip()


def code_text(resource: dict[str, Any]) -> str:
    code = resource.get("code")
    if isinstance(code, dict):
        if code.get("text"):
            return str(code["text"]).strip()
        codings = code.get("coding")
        if isinstance(codings, list) and codings:
            first = codings[0]
            if isinstance(first, dict):
                return str(first.get("display") or first.get("code") or "").strip()
    return resource.get("resourceType", "resource")


def clinical_status(resource: dict[str, Any]) -> str:
    status = resource.get("clinicalStatus")
    if isinstance(status, dict):
        codings = status.get("coding")
        if isinstance(codings, list) and codings:
            first = codings[0]
            if isinstance(first, dict) and first.get("code"):
                return str(first["code"]).strip().lower()
    return str(resource.get("status") or "").strip().lower()


def patient_label(bundle: dict[str, Any]) -> str:
    patient = next(iter_resources(bundle, "Patient"), {})
    names = patient.get("name") if isinstance(patient, dict) else None
    if isinstance(names, list) and names:
        name = names[0]
        if isinstance(name, dict):
            given = " ".join(str(part) for part in name.get("given", []) if part)
            family = str(name.get("family") or "").strip()
            full = " ".join(part for part in [given, family] if part)
            if full:
                return full
    return str(patient.get("id") or "Unknown patient")


def medication_name(resource: dict[str, Any]) -> str:
    concept = resource.get("medicationCodeableConcept")
    if isinstance(concept, dict) and concept.get("text"):
        return str(concept["text"]).strip()
    return text_at(resource, "medicationReference", "display") or "Medication request"


def medication_class_key(name: str) -> str:
    normalized = "".join(char.lower() if char.isalnum() else " " for char in name)
    words = [word for word in normalized.split() if not word.isdigit()]
    return words[0] if words else normalized.strip()


def observation_summary(resource: dict[str, Any]) -> str:
    name = code_text(resource)
    value = text_at(resource, "valueQuantity", "value")
    unit = text_at(resource, "valueQuantity", "unit")
    date = str(resource.get("effectiveDateTime") or "").split("T")[0]
    measured = " ".join(part for part in [value, unit] if part)
    return f"{name}: {measured} on {date}".strip()


def is_high_observation(resource: dict[str, Any]) -> bool:
    quantity = resource.get("valueQuantity")
    ranges = resource.get("referenceRange")
    if not isinstance(quantity, dict) or not isinstance(ranges, list):
        return False
    try:
        value = float(quantity.get("value"))
    except (TypeError, ValueError):
        return False
    for ref in ranges:
        high = ref.get("high") if isinstance(ref, dict) else None
        if isinstance(high, dict):
            try:
                if value > float(high.get("value")):
                    return True
            except (TypeError, ValueError):
                continue
    return False


def medication_safety_findings(medications: list[str], allergies: list[str]) -> list[str]:
    findings = []
    if medications:
        findings.append(f"Medication reconciliation: {len(medications)} active medication requests found.")
    class_counts: dict[str, int] = {}
    for medication in medications:
        key = medication_class_key(medication)
        class_counts[key] = class_counts.get(key, 0) + 1
    duplicates = sorted(key for key, count in class_counts.items() if key and count > 1)
    if duplicates:
        findings.append("Possible duplicate therapy class detected: " + ", ".join(duplicates) + ".")
    else:
        findings.append("No duplicate active medication classes detected in supplied bundle.")
    for allergy in allergies:
        findings.append(f"Allergy alert: {allergy}; verify before new medication orders.")
    return findings or ["No active medication or allergy safety signals found in supplied bundle."]


def care_plan_tasks(careplans: list[dict[str, Any]], high_observations: list[dict[str, Any]], role: str) -> list[str]:
    tasks = []
    for plan in careplans:
        title = str(plan.get("title") or "Active care plan").strip()
        for activity in plan.get("activity", []):
            detail = activity.get("detail") if isinstance(activity, dict) else None
            description = detail.get("description") if isinstance(detail, dict) else None
            if description:
                tasks.append(f"Task candidate from {title}: {description}")
    for observation in high_observations:
        tasks.append(f"Task candidate: follow up {observation_summary(observation)}.")
    if role == "family_caregiver":
        tasks.append("Caregiver handoff: confirm warning signs, medication list, and next appointment date.")
    elif role == "patient":
        tasks.append("Patient handoff: prepare plain-language questions for the next care-team visit.")
    elif role == "care_manager":
        tasks.append("Care manager handoff: assign owner and due date for each follow-up item.")
    else:
        tasks.append("ED handoff: decide what must happen before discharge versus outpatient follow-up.")
    return tasks


def resource_coverage_trace(bundle: dict[str, Any]) -> list[str]:
    counts: dict[str, int] = {}
    for resource in iter_resources(bundle):
        resource_type = str(resource.get("resourceType") or "Unknown")
        counts[resource_type] = counts.get(resource_type, 0) + 1
    trace = [f"{resource_type}: {counts.get(resource_type, 0)}" for resource_type in sorted(REQUIRED_CONTEST_RESOURCES)]
    extras = sorted(set(counts) - REQUIRED_CONTEST_RESOURCES)
    trace.extend(f"{resource_type}: {counts[resource_type]}" for resource_type in extras)
    return trace


def summarize_bundle(bundle: dict[str, Any], role: str = "ed_doctor") -> FhirSummary:
    selected_role = role.lower().strip()
    if selected_role not in ROLE_GUIDANCE:
        raise ValueError(f"Unknown role {role!r}; choose one of {', '.join(sorted(ROLE_GUIDANCE))}")

    active_conditions = [
        code_text(resource)
        for resource in iter_resources(bundle, "Condition")
        if clinical_status(resource) in {"active", "recurrence", "relapse"}
    ]
    active_medication_resources = [
        resource
        for resource in iter_resources(bundle, "MedicationRequest")
        if str(resource.get("status") or "").lower() == "active"
    ]
    active_meds = [medication_name(resource) for resource in active_medication_resources]
    allergies = [code_text(resource) for resource in iter_resources(bundle, "AllergyIntolerance")]
    observations = list(iter_resources(bundle, "Observation"))
    high_observation_resources = [resource for resource in observations if is_high_observation(resource)]
    high_observations = [observation_summary(resource) for resource in high_observation_resources]
    encounters = list(iter_resources(bundle, "Encounter"))
    careplans = list(iter_resources(bundle, "CarePlan"))

    current_issues = []
    current_issues.extend(f"Active condition: {item}" for item in active_conditions)
    current_issues.extend(f"Active medication: {item}" for item in active_meds)
    if allergies:
        current_issues.append("Known allergy/intolerance: " + ", ".join(allergies))

    recent_changes = []
    for encounter in encounters:
        reason = ""
        reasons = encounter.get("reasonCode")
        if isinstance(reasons, list) and reasons:
            reason = str(reasons[0].get("text") or "").strip() if isinstance(reasons[0], dict) else ""
        start = text_at(encounter, "period", "start").split("T")[0]
        recent_changes.append(f"Recent encounter {start}: {reason or encounter.get('status', 'recorded')}")
    recent_changes.extend(high_observations)

    risks = []
    risks.extend(f"Follow up abnormal observation: {item}" for item in high_observations)
    for plan in careplans:
        title = str(plan.get("title") or "Active care plan").strip()
        for activity in plan.get("activity", []):
            detail = activity.get("detail") if isinstance(activity, dict) else None
            description = detail.get("description") if isinstance(detail, dict) else None
            if description:
                risks.append(f"{title}: {description}")
    if allergies:
        risks.append("Medication safety check should account for allergies before new orders.")

    if selected_role == "care_manager":
        risks.append("Confirm medication adherence and schedule follow-up for abnormal chronic disease markers.")
    elif selected_role == "patient":
        risks.append("Ask the care team what the high readings mean and when to repeat testing.")
    elif selected_role == "family_caregiver":
        risks.append("Watch for dizziness, medication side effects, and missed follow-up appointments.")
    else:
        risks.append("Prioritize acute causes for symptoms and reconcile meds before discharge.")

    return FhirSummary(
        patient_label=patient_label(bundle),
        role=ROLE_GUIDANCE[selected_role]["label"],
        current_issues=current_issues or ["No active issues found in supplied bundle."],
        recent_changes=recent_changes or ["No recent encounter or observation changes found."],
        risks_follow_up=risks or ["No follow-up risks generated from supplied bundle."],
        medication_safety=medication_safety_findings(active_meds, allergies),
        care_plan_next_steps=care_plan_tasks(careplans, high_observation_resources, selected_role),
        evidence_trace=resource_coverage_trace(bundle),
    )


def render_markdown(summary: FhirSummary) -> str:
    lines = [
        f"# FHIR Patient Summary - {summary.role}",
        "",
        f"Patient: {summary.patient_label}",
        "",
        "## Current Issues",
        "",
        *[f"- {item}" for item in summary.current_issues],
        "",
        "## Recent Changes",
        "",
        *[f"- {item}" for item in summary.recent_changes],
        "",
        "## Risks / Follow-Up Items",
        "",
        *[f"- {item}" for item in summary.risks_follow_up],
        "",
        "## Medication Safety",
        "",
        *[f"- {item}" for item in summary.medication_safety],
        "",
        "## Care Plan Next Steps",
        "",
        *[f"- {item}" for item in summary.care_plan_next_steps],
        "",
        "## Evidence Trace",
        "",
        *[f"- {item}" for item in summary.evidence_trace],
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bundle", type=Path, default=SAMPLE_BUNDLE)
    parser.add_argument("--role", default="ed_doctor", choices=sorted(ROLE_GUIDANCE))
    parser.add_argument("--json-output", type=Path)
    parser.add_argument("--markdown-output", type=Path)
    args = parser.parse_args()

    summary = summarize_bundle(load_bundle(args.bundle), args.role)
    if args.json_output:
        args.json_output.write_text(json.dumps(summary.as_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown = render_markdown(summary)
    if args.markdown_output:
        args.markdown_output.write_text(markdown, encoding="utf-8")
    else:
        print(markdown)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

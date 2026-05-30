from __future__ import annotations

import unittest

from rewardops_guard.delivery_kits.intersystems_fhir_agent_pack.contest_packet import (
    APPROVAL_GATES,
    build_packet,
)
from rewardops_guard.delivery_kits.intersystems_fhir_agent_pack.contest_preflight import build_report
from rewardops_guard.delivery_kits.intersystems_fhir_agent_pack.fhir_summary_agent import (
    load_bundle,
    render_markdown,
    summarize_bundle,
)


class FhirSummaryAgentTests(unittest.TestCase):
    def test_summary_uses_required_fhir_resources(self) -> None:
        summary = summarize_bundle(load_bundle(), "ed_doctor")
        joined = "\n".join(summary.current_issues + summary.recent_changes + summary.risks_follow_up)
        self.assertIn("Type 2 diabetes", joined)
        self.assertIn("Metformin", joined)
        self.assertIn("Penicillin", joined)
        self.assertIn("Hemoglobin A1c", joined)
        self.assertIn("Recent encounter", joined)
        self.assertIn("Diabetes and hypertension follow-up", joined)
        self.assertIn("Medication reconciliation", " ".join(summary.medication_safety))
        self.assertIn("Task candidate", " ".join(summary.care_plan_next_steps))
        self.assertIn("MedicationRequest: 2", " ".join(summary.evidence_trace))

    def test_role_specific_followup_changes(self) -> None:
        bundle = load_bundle()
        patient = summarize_bundle(bundle, "patient")
        care_manager = summarize_bundle(bundle, "care_manager")
        self.assertIn("Ask the care team", " ".join(patient.risks_follow_up))
        self.assertIn("Confirm medication adherence", " ".join(care_manager.risks_follow_up))

    def test_markdown_has_expected_sections(self) -> None:
        markdown = render_markdown(summarize_bundle(load_bundle(), "ed_doctor"))
        self.assertIn("## Current Issues", markdown)
        self.assertIn("## Recent Changes", markdown)
        self.assertIn("## Risks / Follow-Up Items", markdown)
        self.assertIn("## Medication Safety", markdown)
        self.assertIn("## Care Plan Next Steps", markdown)
        self.assertIn("## Evidence Trace", markdown)

    def test_contest_packet_preserves_prize_and_gates(self) -> None:
        packet = build_packet()
        self.assertEqual(packet["prize_context"]["expert_first_place_usd"], 5000)
        self.assertEqual(packet["prize_context"]["total_pool_usd"], 12000)
        gates = " ".join(APPROVAL_GATES).lower()
        self.assertIn("identity verification", gates)
        self.assertIn("public github", gates)
        self.assertIn("real patient data", gates)
        self.assertIn("social", gates)
        self.assertIn("bonus_context", packet)
        self.assertIn("contest_preflight.py", " ".join(item["path"] for item in packet["local_artifacts"]))

    def test_family_caregiver_role_and_preflight(self) -> None:
        caregiver = summarize_bundle(load_bundle(), "family_caregiver")
        self.assertIn("caregiver", caregiver.role.lower())
        self.assertIn("Caregiver handoff", " ".join(caregiver.care_plan_next_steps))
        report = build_report()
        self.assertTrue(report["local_ok"])
        self.assertFalse(report["external_submission_ok"])
        self.assertIn("Open Exchange", " ".join(report["external_blockers_before_contest_submission"]))
        packaging = {item["name"]: item["ok"] for item in report["packaging_checks"]}
        self.assertTrue(packaging["iris_health_container_image"])
        self.assertTrue(packaging["zpm_resource_package"])
        self.assertTrue(packaging["objectscript_bridge_class"])

    def test_unknown_role_rejected(self) -> None:
        with self.assertRaises(ValueError):
            summarize_bundle(load_bundle(), "administrator")


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import threading
import unittest
from urllib.parse import urlparse

from rewardops_guard.delivery_kits.intersystems_fhir_agent_pack.contest_packet import (
    APPROVAL_GATES,
    build_packet,
)
from rewardops_guard.delivery_kits.intersystems_fhir_agent_pack.contest_preflight import build_report
from rewardops_guard.delivery_kits.intersystems_fhir_agent_pack.demo_server import render_demo_html, selected_role
from rewardops_guard.delivery_kits.intersystems_fhir_agent_pack.fhir_summary_agent import (
    FHIR_SEARCH_RESOURCES,
    fetch_patient_bundle,
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

    def test_demo_html_has_roles_and_json_endpoint_hint(self) -> None:
        summary = summarize_bundle(load_bundle(), "care_manager")
        html = render_demo_html(summary, "care_manager")
        self.assertIn("FHIR Care Brief Agent", html)
        self.assertIn("/summary.json?role=care_manager", html)
        self.assertIn("Medication Safety", html)
        self.assertEqual(selected_role("/?role=patient"), "patient")
        self.assertEqual(selected_role("/?role=unknown"), "ed_doctor")

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
        self.assertIn("demo_server.py", " ".join(item["path"] for item in packet["local_artifacts"]))

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
        self.assertTrue(packaging["open_exchange_submission_draft"])
        self.assertTrue(packaging["developer_community_article_draft"])
        self.assertTrue(packaging["local_web_demo"])
        self.assertTrue(packaging["local_demo_screenshots"])

    def test_fetch_patient_bundle_from_read_only_fhir_server(self) -> None:
        sample_bundle = load_bundle()
        resources_by_type: dict[str, list[dict[str, object]]] = {}
        for entry in sample_bundle["entry"]:
            resource = entry["resource"]
            resources_by_type.setdefault(resource["resourceType"], []).append(resource)

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self) -> None:
                parsed = urlparse(self.path)
                if parsed.path == "/fhir/Patient/patient-001":
                    self.send_json(resources_by_type["Patient"][0])
                    return
                resource_type = parsed.path.rsplit("/", 1)[-1]
                if resource_type in FHIR_SEARCH_RESOURCES:
                    self.send_json(
                        {
                            "resourceType": "Bundle",
                            "type": "searchset",
                            "entry": [{"resource": resource} for resource in resources_by_type.get(resource_type, [])],
                        }
                    )
                    return
                self.send_response(404)
                self.end_headers()

            def log_message(self, format: str, *args: object) -> None:
                return

            def send_json(self, data: dict[str, object]) -> None:
                payload = json.dumps(data).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/fhir+json")
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)

        server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            base_url = f"http://127.0.0.1:{server.server_port}/fhir"
            fetched = fetch_patient_bundle(base_url, "patient-001")
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)

        summary = summarize_bundle(fetched, "ed_doctor")
        self.assertIn("Alex Rivera", summary.patient_label)
        self.assertIn("MedicationRequest: 2", " ".join(summary.evidence_trace))

    def test_unknown_role_rejected(self) -> None:
        with self.assertRaises(ValueError):
            summarize_bundle(load_bundle(), "administrator")


if __name__ == "__main__":
    unittest.main()

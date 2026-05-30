# InterSystems FHIR Contest Preflight

Checked: 2026-05-30T13:42:51+00:00
Local OK: `true`
External submission OK: `false`
First-place target: `$5000`
Deadline: 2026-06-07 23:59 EST

## Resource Coverage

- present: AllergyIntolerance
- present: CarePlan
- present: Condition
- present: Encounter
- present: MedicationRequest
- present: Observation
- present: Patient

## Role Checks

- ok: care_manager
- ok: ed_doctor
- ok: family_caregiver
- ok: patient

## Packaging Checks

- ok: iris_health_container_image - Dockerfile references InterSystems IRIS for Health Community image
- ok: docker_build_smoke_command - Dockerfile runs the synthetic FHIR summary agent during image build
- ok: docker_compose_service - docker-compose.yml exposes the standard local IRIS web port
- ok: zpm_module_name - module.xml declares fhir-care-brief-agent
- ok: zpm_resource_package - module.xml packages RewardOps.FHIR classes
- ok: zpm_csp_application - module.xml declares /fhir-care-brief-agent web app
- ok: objectscript_bridge_class - ObjectScript package bridge class is present
- ok: open_exchange_submission_draft - Open Exchange submission draft is present but not submitted
- ok: developer_community_article_draft - Developer Community article draft is present but not published
- ok: local_web_demo - Dependency-free local web demo with JSON endpoint is present
- ok: local_demo_screenshots - Desktop and mobile local demo screenshots are present
- ok: local_submission_bundle_builder - Local ZIP bundle builder with manifest generation is present

## External Blockers

- Create or log into InterSystems Developer Community / Open Exchange account
- Publish the app as an open-source GitHub or GitLab repository
- Publish the app on InterSystems Open Exchange
- Apply the Open Exchange app to the contest before 2026-06-07 23:59 EST
- Provide prize identity information if InterSystems requests it
- Approve any public video/article/demo publication

# InterSystems FHIR Agent Packet

Generated: 2026-05-30T13:35:14+00:00
Project: FHIR Care Brief Agent
Expert first-place fit: $5000
Submission deadline: 2026-06-07 23:59 EST

## Angle

A synthetic-data-first FHIR agent that turns local or read-only server FHIR resources into role-specific care summaries.

Matches the Smart Patient Summary Generator bonus idea and now includes medication-safety, care-plan navigator, read-only FHIR REST fetching, Docker, ZPM/IPM packaging, local web demo, screenshot assets, and submission/article drafts for a stronger expert-judging story.

## Agent Workflow

- Load an approved FHIR Bundle or fetch a patient-centered Bundle from an approved read-only FHIR REST base URL.
- Extract active clinical signals from the required resources.
- Generate current issues, recent changes, and risks/follow-up items.
- Generate medication-safety findings, care-plan task candidates, and evidence traceability.
- Render role-specific outputs for ED doctor, care manager, patient, or family caregiver.
- Ship Docker, docker-compose, module.xml, and a minimal RewardOps.FHIR ObjectScript bridge class for IRIS/Open Exchange packaging review.
- Expose a dependency-free local web demo with HTML dashboard and /summary.json endpoint.
- Package desktop and mobile screenshots for quick visual review.
- Prepare Open Exchange submission and Developer Community article drafts without publishing them.
- Block PHI, account, publication, video, KYC, spend, wallet, and social steps until approved.

## Suggested Contest Ideas Covered

- Smart Patient Summary Generator
- Medication Safety and Interaction Assistant
- AI-Powered Care Plan Navigator

## Local Artifacts

- ready: `rewardops_guard/delivery_kits/intersystems_fhir_agent_pack/README.md`
- ready: `rewardops_guard/delivery_kits/intersystems_fhir_agent_pack/SUBMISSION_DRAFT.md`
- ready: `rewardops_guard/delivery_kits/intersystems_fhir_agent_pack/ARTICLE_DRAFT.md`
- ready: `rewardops_guard/delivery_kits/intersystems_fhir_agent_pack/Dockerfile`
- ready: `rewardops_guard/delivery_kits/intersystems_fhir_agent_pack/docker-compose.yml`
- ready: `rewardops_guard/delivery_kits/intersystems_fhir_agent_pack/module.xml`
- ready: `rewardops_guard/delivery_kits/intersystems_fhir_agent_pack/fhir_summary_agent.py`
- ready: `rewardops_guard/delivery_kits/intersystems_fhir_agent_pack/demo_server.py`
- ready: `rewardops_guard/delivery_kits/intersystems_fhir_agent_pack/demo_assets/README.md`
- ready: `rewardops_guard/delivery_kits/intersystems_fhir_agent_pack/demo_assets/care_brief_demo_desktop.png`
- ready: `rewardops_guard/delivery_kits/intersystems_fhir_agent_pack/demo_assets/care_brief_demo_mobile.png`
- ready: `rewardops_guard/delivery_kits/intersystems_fhir_agent_pack/contest_preflight.py`
- ready: `rewardops_guard/delivery_kits/intersystems_fhir_agent_pack/sample_patient_bundle.json`
- ready: `rewardops_guard/delivery_kits/intersystems_fhir_agent_pack/sample_summary_ed_doctor.json`
- ready: `rewardops_guard/delivery_kits/intersystems_fhir_agent_pack/sample_summary_ed_doctor.md`
- ready: `rewardops_guard/delivery_kits/intersystems_fhir_agent_pack/src/cls/RewardOps/FHIR/CareBriefAgent.cls`
- ready: `rewardops_guard/delivery_kits/intersystems_fhir_agent_pack/test_fhir_summary_agent.py`

## Approval Gates

- InterSystems Developer Community / Open Exchange account creation or login
- Public GitHub/GitLab repository publication
- Demo video recording or upload
- Open Exchange contest submission
- Identity verification for cash prize collection
- Real patient data, PHI, credentials, cloud deployment, paid API spend, wallet action, or social posting

## Sources

- https://community.intersystems.com/post/intersystems-programming-contest-ai-agents-fhir
- https://community.intersystems.com/post/technology-bonuses-intersystems-programming-contest-ai-agents-fhir
- https://openexchange.intersystems.com/contests?archive=1

Local ready: `true`

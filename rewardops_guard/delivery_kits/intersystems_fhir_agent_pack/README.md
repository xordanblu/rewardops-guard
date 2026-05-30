# InterSystems FHIR Agent Pack

Local package for the InterSystems Programming Contest: AI Agents for FHIR.
It prepares a synthetic-data-first `FHIR Care Brief Agent` without creating an
InterSystems account, publishing a repository, uploading a video, using real
patient data, or submitting to Open Exchange.

## What It Builds

- Role-specific patient summaries for ED doctor, care manager, and patient.
- Current issues from `Condition`, `MedicationRequest`, and `AllergyIntolerance`.
- Recent changes from `Encounter` and abnormal `Observation` resources.
- Follow-up items from abnormal observations, allergies, and `CarePlan` tasks.
- Medication-safety findings, duplicate therapy checks, and allergy alerts.
- Care-plan task candidates for clinician handoff and patient follow-up.
- Evidence traceability showing required FHIR resource coverage.
- Read-only FHIR REST fetch path for approved synthetic/test servers.
- Docker and `docker-compose.yml` scaffold for IRIS for Health Community review.
- `module.xml` and `RewardOps.FHIR.CareBriefAgent` ObjectScript bridge for
  ZPM/IPM packaging review.
- Open Exchange submission draft and Developer Community article draft.
- Dependency-free local web demo with HTML dashboard and `/summary.json`.
- Desktop and mobile screenshot assets under `demo_assets/`.
- A contest packet that preserves prize/deadline context and approval gates.

## Run

```bash
python3 rewardops_guard/delivery_kits/intersystems_fhir_agent_pack/fhir_summary_agent.py --role ed_doctor
python3 rewardops_guard/delivery_kits/intersystems_fhir_agent_pack/fhir_summary_agent.py --role family_caregiver
python3 rewardops_guard/delivery_kits/intersystems_fhir_agent_pack/contest_preflight.py
python3 rewardops_guard/delivery_kits/intersystems_fhir_agent_pack/contest_packet.py
python3 rewardops_guard/delivery_kits/intersystems_fhir_agent_pack/demo_server.py --port 8765
python3 -m unittest rewardops_guard.delivery_kits.intersystems_fhir_agent_pack.test_fhir_summary_agent -v
```

For an approved synthetic/test FHIR server:

```bash
python3 rewardops_guard/delivery_kits/intersystems_fhir_agent_pack/fhir_summary_agent.py \
  --fhir-base-url http://localhost:52773/fhir/r4 \
  --patient-id patient-001 \
  --role ed_doctor
```

From this kit directory, validate the container configuration without starting
IRIS:

```bash
docker compose config
```

## Contest Fit

The current package targets the official Smart Patient Summary Generator idea
and adds adjacent Medication Safety and Care Plan Navigator behavior. It also
adds Docker and ZPM/IPM packaging artifacts so reviewers can inspect the IRIS
deployment path. The local preflight checks required FHIR resources, role
outputs, README/package presence, packaging files, and the external gates that
still need human approval before public submission.

## Submission Boundary

This kit is local only. Public contest submission still needs explicit approval
for account creation/login, public repo publication, video upload, Open Exchange
submission, identity verification for prize collection, and any use of real PHI
or external credentials.

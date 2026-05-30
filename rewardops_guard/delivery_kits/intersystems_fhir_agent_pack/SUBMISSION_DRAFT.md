# Open Exchange Submission Draft

## Application Name

FHIR Care Brief Agent

## Short Description

Synthetic-data-first AI agent that reads FHIR resources and produces role-specific
clinical care briefs with medication safety, care-plan tasks, and evidence
traceability.

## Long Description

FHIR Care Brief Agent targets the InterSystems Programming Contest: AI Agents for
FHIR. It implements the Smart Patient Summary Generator idea and extends it with
Medication Safety and Care Plan Navigator behavior. The agent can load a local
FHIR Bundle or fetch an approved patient-centered bundle from a read-only FHIR
REST base URL. It summarizes Patient, Condition, MedicationRequest,
AllergyIntolerance, Observation, Encounter, and CarePlan resources for ED
doctors, care managers, patients, and family caregivers.

The package is intentionally synthetic-data-first. It includes a sample bundle,
sample output, Docker and docker-compose scaffolding for IRIS for Health
Community review, a ZPM/IPM `module.xml`, and a minimal ObjectScript bridge
class under `RewardOps.FHIR`.

## Key Features

- Patient summary generator with current issues, recent changes, and follow-up
  risks.
- Medication reconciliation, duplicate therapy checks, and allergy alerts.
- Care-plan task candidates for clinician handoff and patient follow-up.
- Evidence traceability showing which FHIR resources drove each run.
- Read-only FHIR REST fetch path for approved synthetic/test servers.
- Docker/ZPM packaging scaffold for InterSystems review.

## Demo Commands

```bash
python3 rewardops_guard/delivery_kits/intersystems_fhir_agent_pack/fhir_summary_agent.py --role ed_doctor
python3 rewardops_guard/delivery_kits/intersystems_fhir_agent_pack/fhir_summary_agent.py --role family_caregiver
python3 rewardops_guard/delivery_kits/intersystems_fhir_agent_pack/contest_preflight.py
docker compose -f rewardops_guard/delivery_kits/intersystems_fhir_agent_pack/docker-compose.yml config
```

## Submission Boundary

This draft has not been submitted to Open Exchange. Public submission, account
creation/login, identity verification, public video/article publication, cloud
deployment, and any use of real PHI require explicit human approval.

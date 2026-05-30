# Building a Synthetic-Data-First FHIR Care Brief Agent

The InterSystems AI Agents for FHIR contest rewards useful agent workflows that
operate inside FHIR interoperability solutions. I built FHIR Care Brief Agent as
a compact, reviewable package around a practical clinical workflow: turning a
patient-centered FHIR bundle into a role-specific care brief.

The agent uses synthetic FHIR data by default. It works with Patient, Condition,
MedicationRequest, AllergyIntolerance, Observation, Encounter, and CarePlan
resources. For each run, it generates current issues, recent changes,
risks/follow-up items, medication-safety notes, care-plan task candidates, and
an evidence trace that shows which resources were present.

## Why This Shape

The Smart Patient Summary Generator idea is useful because clinicians and care
teams need different slices of the same patient context. An ED doctor needs
acute risks and discharge blockers. A care manager needs follow-up owners and
care gaps. A patient or family caregiver needs plain-language next steps.

FHIR Care Brief Agent keeps those role differences explicit while remaining
small enough for judges to inspect quickly.

## FHIR Server Path

The package can run from a local bundle or from a read-only FHIR REST base URL:

```bash
python3 rewardops_guard/delivery_kits/intersystems_fhir_agent_pack/fhir_summary_agent.py \
  --fhir-base-url http://localhost:52773/fhir/r4 \
  --patient-id patient-001 \
  --role ed_doctor
```

No credentials are included. The FHIR server path is intended for approved
synthetic or test data only.

## Packaging

The repo includes Docker, docker-compose, `module.xml`, and a minimal
`RewardOps.FHIR.CareBriefAgent` ObjectScript bridge class. The local preflight
validates these files along with the FHIR resource coverage and role outputs.

## Safety Boundary

The project is designed to avoid real PHI by default. It does not submit to Open
Exchange, upload videos, create accounts, or handle prize identity verification
without explicit approval.

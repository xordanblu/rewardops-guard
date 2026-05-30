FROM intersystemsdc/irishealth-community:latest

USER root
WORKDIR /irisdev/app

COPY . /irisdev/app

RUN python3 /irisdev/app/fhir_summary_agent.py \
    --role ed_doctor \
    --json-output /tmp/fhir-care-brief-ed-doctor.json \
    --markdown-output /tmp/fhir-care-brief-ed-doctor.md

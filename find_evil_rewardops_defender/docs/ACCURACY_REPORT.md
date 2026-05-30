# Accuracy Report

Status: local prep only. This report summarizes the current deterministic test
evidence for the FIND EVIL judging packet.

## Scope

RewardOps Defender currently validates two local sanitized datasets:

- `dfir_triage_agent/sample_events.jsonl`
- `dfir_triage_agent/sample_agent_events.jsonl`
- `cases/find_evil_local_case.json`

Both datasets are synthetic and contain no private credentials, personal
records, live target data, or production system artifacts.

## Reproduction Commands

```bash
python3 -m unittest discover -s tests
./run_terminal_demo.sh
```

The demo regenerates these reviewer-facing reports:

- `out/dfir_triage_report.json`
- `out/dfir_triage_report.md`
- `out/rewardops_defender_report.json`
- `out/rewardops_defender_report.md`
- `out/submission_guard_manifest.json`
- `out/find_evil_case_report.json`
- `out/find_evil_case_report.md`

## DFIR Triage Accuracy

The DFIR sample contains five events. Four events include labelled
`expected_rules`; one event is a self-correction probe that should not remain a
public egress finding.

Current deterministic result:

| Metric | Value |
| --- | ---: |
| Event count | 5 |
| Finding count | 5 |
| Highest severity | critical |
| Labelled events | 4 |
| Precision | 1.0 |
| Recall | 1.0 |
| Missed rules | 0 |
| Unexpected rules | 0 |
| Self-corrections | 1 |

Validated rule labels:

- `encodedcommand`
- `external_connection`
- `failed_login`
- `payload.dll`
- `appdata`

## Agent-Defense Sequence Accuracy

The agent-defense sample contains six events covering hostile prompt text,
wallet-signing traps, encoded endpoint execution, credential access, outbound
transfer, and benign training context.

Current deterministic result:

| Metric | Value |
| --- | ---: |
| Event count | 6 |
| High/critical event count | 4 |
| Self-corrections | 2 |
| Verdict | agent_tool_abuse+credential_theft_with_exfiltration+scripted_execution_chain |

Validated sequence hypotheses:

- `agent_tool_abuse`: external content attempted prompt disclosure or
  payment-capable approval.
- `credential_theft_with_exfiltration`: credential material access and
  outbound upload appeared in the same host timeline.
- `scripted_execution_chain`: encoded shell activity preceded higher-risk
  endpoint and network signals.

## Labelled FIND EVIL Local Case

The local case contains seven events with explicit ground truth labels. It adds
an obfuscated prompt-smuggling event to the agent-defense sequence and verifies
that the benign training reference is self-corrected rather than counted as a
malicious side-effect.

Current deterministic result:

| Metric | Value |
| --- | ---: |
| Event count | 7 |
| Expected malicious events | 6 |
| Detected malicious events | 6 |
| False positives | 0 |
| False negatives | 0 |
| Precision | 1.0 |
| Recall | 1.0 |
| True negative/self-corrected benign adjustments | 1 |

Validated ground-truth hypotheses:

- `agent_tool_abuse`
- `credential_theft_with_exfiltration`
- `scripted_execution_chain`

## False Positives

Known corrected false positives:

- A private/reserved network destination is removed from public-egress
  findings and recorded as a correction.
- Training or documentation text containing attack keywords is downgraded when
  no tool side effect occurred.

Known residual false-positive risk:

- Keyword-based rules can over-score unfamiliar benign admin tooling until
  more labelled data is added.
- Synthetic evidence does not include noisy enterprise logs, so production
  precision is not proven by this demo.

## Missed Artifacts

Known missed-artifact risk:

- The current parser does not extract disk-image offsets, memory addresses, or
  packet-level network fields.
- The MCP-style wrapper accepts JSONL events rather than directly mounting SIFT
  images.
- Broader malware families, cloud-control-plane logs, browser artifacts, and
  EDR schemas are out of scope for this first package.

## Hallucination Controls

The agent does not invent raw evidence. Reports only include:

- normalized event fields from the input files;
- deterministic redacted hashes;
- explicit rule IDs matched by local code;
- correction records produced by deterministic code paths;
- response-plan steps that are marked as approval-gated when they would affect
  real systems.

If an input event lacks evidence for a claim, the report cannot cite a hash or
matched rule for that claim. This keeps unsupported conclusions visible during
review.

## Evidence Integrity

The demo is read-only:

- Input files are read from local JSONL.
- Output reports are written to `out/`.
- Original input events are not modified.
- Raw hostile prompt text is hashed before reporting.
- Token-like values and email-like values are redacted before hash/report
  generation in the DFIR triage path.
- No live probing, exploit execution, wallet signing, credential use,
  destructive remediation, account creation, or public submission is performed.

## Publication Guard

`dfir_triage_agent/submission_guard.py` scans the release package before a
public upload. It produces `out/submission_guard_manifest.json` with file
hashes, scanned text-file counts, prompt-injection fixture counts, and blocking
secret findings.

The guard treats hostile text such as "ignore previous instructions" or
requests to reveal system prompts as evidence fixtures only. Those strings are
counted in the manifest, but they are never executed, followed, submitted, or
copied into hidden agent context. The package is considered `release_ready`
only when no blocking secret patterns are found.

## Current Claim Boundary

This package proves deterministic local behavior on the included sanitized
datasets. It does not claim production-grade incident response coverage until
additional SIFT-native evidence parsers, real-world labelled datasets, and
cross-platform terminal verification are added.

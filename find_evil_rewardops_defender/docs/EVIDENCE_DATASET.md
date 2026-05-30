# FIND EVIL Evidence Dataset Draft

Status: local prep only. This is a synthetic, non-sensitive dataset for terminal demonstration and judging readiness.

## Dataset

- Source file: `rewardops_guard/delivery_kits/dfir_triage_agent/sample_events.jsonl`
- Agent-defense source file: `dfir_triage_agent/sample_agent_events.jsonl`
- Labelled FIND EVIL case file: `cases/find_evil_local_case.json`
- Format: JSONL security events.
- DFIR event count: 5.
- Agent-defense event count: 6.
- Labelled FIND EVIL event count: 7.
- Labels: `expected_rules` are included for four events; the fifth event is a self-correction probe with no expected finding.

## Covered Evidence Types

- Endpoint process execution: encoded PowerShell.
- Network connection: public destination egress.
- Authentication: repeated failed login.
- File write: suspicious DLL in user profile persistence path.
- Correction probe: private network destination that should not remain flagged as public egress.
- Agent prompt injection: request to paste internal developer instructions.
- Obfuscated prompt smuggling: spaced/leetspeak request to copy developer instructions and tool schema.
- Wallet trap: request to connect/sign for automatic reward release.
- Credential exfiltration: SAM save followed by outbound upload.
- Benign context: training document phrase that should be downgraded.

## Ground Truth Labels

- `encodedcommand`
- `external_connection`
- `failed_login`
- `payload.dll`
- `appdata`

## Local Run Evidence

```text
python3 rewardops_guard/delivery_kits/dfir_triage_agent/dfir_triage.py \
  --events rewardops_guard/delivery_kits/dfir_triage_agent/sample_events.jsonl \
  --json-output outputs/manual-20260529-find-evil/dfir_triage_report.json \
  --markdown-output outputs/manual-20260529-find-evil/dfir_triage_report.md \
  --case-id find-evil-demo

{"event_count": 5, "finding_count": 5, "severity": "critical"}
```

## Accuracy Result

- Status: validated.
- Labelled events: 4.
- Precision: 1.0.
- Recall: 1.0.
- Missed rules: 0.
- Unexpected rules: 0.
- Self-corrections: 1 private-network egress false positive removed.

## Agent-Defense Result

```text
python3 dfir_triage_agent/rewardops_defender.py \
  --events dfir_triage_agent/sample_agent_events.jsonl \
  --json-output out/rewardops_defender_report.json \
  --markdown-output out/rewardops_defender_report.md \
  --case-id find-evil-agent-defense

{"event_count": 6, "high_event_count": 4, "verdict": "agent_tool_abuse+credential_theft_with_exfiltration+scripted_execution_chain"}
```

- Prompt-injection and wallet-signing lures are high risk.
- Credential access plus outbound transfer becomes a high-confidence hypothesis.
- Training-document attack phrases are self-corrected to low risk.
- Raw event details are hashed and are not stored in the report.

## Labelled FIND EVIL Local Case

```text
python3 dfir_triage_agent/case_runner.py \
  --case-json cases/find_evil_local_case.json \
  --json-output out/find_evil_case_report.json \
  --markdown-output out/find_evil_case_report.md

{"case_id": "rewardops-find-evil-local-001", "passes_ground_truth": true, "event_precision": 1.0, "event_recall": 1.0}
```

The case includes labels for expected signals and expected hypotheses so the
precision/recall score is reproducible:

- expected malicious events: 6;
- detected malicious events: 6;
- false positives: 0;
- false negatives: 0;
- event precision: 1.0000;
- event recall: 1.0000;
- true negative/self-corrected benign adjustments: 1.

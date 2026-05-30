# DFIR Triage Report

Generated: 2026-05-30T12:58:16Z
Case: find-evil-demo
Severity: critical
Events: 5
Findings: 5

## Containment Checklist

- Isolate host and collect PowerShell transcript/logs.
- Block destination pending reputation review.
- Check source reputation and enforce MFA/session review.
- Quarantine file and hash it in a sandboxed workflow.
- Review Run keys, startup folders, and scheduled tasks.

## Timeline

- 2026-05-29T01:02:03Z `workstation-17` process_start: PowerShell encoded command (982ee5cfccd0)
- 2026-05-29T01:05:12Z `workstation-17` network_connection: External network connection (8c8190b68440)
- 2026-05-29T01:08:22Z `workstation-17` failed_login: Repeated failed login (5a922e241a78)
- 2026-05-29T01:11:55Z `workstation-17` file_write: Suspicious payload write, User-profile persistence path (fe4b96c402ae)
- 2026-05-29T01:15:05Z `workstation-17` network_connection: no triggered rule (8fb2b0fe7c52)

## Accuracy Report

- Status: validated
- Labelled events: 4
- Precision: 1.0
- Recall: 1.0
- Missed rules: 0
- Unexpected rules: 0

## Self-Correction

- external_connection: destination is non-public or reserved test evidence, so it is not treated as internet egress (8fb2b0fe7c52)

## Audit Trail

- Step 1: process_start hash=982ee5cfccd0 rules=encodedcommand corrections=0
- Step 2: network_connection hash=8c8190b68440 rules=external_connection corrections=0
- Step 3: failed_login hash=5a922e241a78 rules=failed_login corrections=0
- Step 4: file_write hash=fe4b96c402ae rules=payload.dll,appdata corrections=0
- Step 5: network_connection hash=8fb2b0fe7c52 rules=none corrections=1

## Safe Boundaries

- Defensive triage only; no exploitation, live probing, credential use, or malware execution.
- Emails and token-like values are redacted before reporting.
- Event hashes are over redacted canonical event data for reproducible evidence tracking.

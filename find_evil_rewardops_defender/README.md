# RewardOps Defender

RewardOps Defender is a local, read-only incident-response and agent-security
prototype for the FIND EVIL hackathon. It turns sanitized JSONL security events
into traceable reports with severity, finding timelines, self-correction
records, accuracy validation, and deterministic audit trails.

The project is intentionally terminal-first: no cloud account, live endpoint,
credential, wallet, social account, or production system is required for the
demo.

## Why It Exists

Autonomous attackers can move faster than manual command-line triage. This
prototype gives an analyst a bounded defensive agent loop:

1. Load sanitized case events.
2. Score them with transparent rules.
3. Correct likely false positives.
4. Compare findings against labelled expected rules when available.
5. Export reviewer-readable JSON and Markdown evidence.

It also models a hostile autonomous-agent sequence: prompt-injection lures,
wallet-signing traps, encoded endpoint execution, credential access, and
exfiltration are scored together as one investigation path.

## Quick Start

```bash
python3 -m unittest discover -s tests

python3 dfir_triage_agent/dfir_triage.py \
  --events dfir_triage_agent/sample_events.jsonl \
  --json-output out/dfir_triage_report.json \
  --markdown-output out/dfir_triage_report.md \
  --case-id find-evil-demo

python3 dfir_triage_agent/rewardops_defender.py \
  --events dfir_triage_agent/sample_agent_events.jsonl \
  --json-output out/rewardops_defender_report.json \
  --markdown-output out/rewardops_defender_report.md \
  --case-id find-evil-agent-defense

python3 dfir_triage_agent/submission_guard.py \
  --root . \
  --json-output out/submission_guard_manifest.json

python3 dfir_triage_agent/case_runner.py \
  --case-json cases/find_evil_local_case.json \
  --json-output out/find_evil_case_report.json \
  --markdown-output out/find_evil_case_report.md

python3 submission/devpost_preflight.py
```

Expected summary:

```text
{"event_count": 5, "finding_count": 5, "severity": "critical"}
{"event_count": 6, "high_event_count": 4, "verdict": "agent_tool_abuse+credential_theft_with_exfiltration+scripted_execution_chain"}
{"blocking_findings": 0, "file_count": 45, "injection_fixture_count": 26, "verdict": "release_ready"}
{"case_id": "rewardops-find-evil-local-001", "passes_ground_truth": true, "event_precision": 1.0, "event_recall": 1.0}
{"status": "ready_for_external_submission", "local_ok": true, "external_submission_ok": false, "local_blocking": 0, "external_blocking": 2}
```

## JSON-RPC Tool Wrapper

```bash
python3 -m dfir_triage_agent.mcp_server --oneshot \
  '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"triage_case","arguments":{"path":"dfir_triage_agent/sample_events.jsonl","case_id":"find-evil-mcp"}}}'
```

Tools:

- `load_case_events`
- `triage_case`
- `explain_evidence`
- `export_report`

## Agent-Defense Sequence

`dfir_triage_agent/rewardops_defender.py` demonstrates the FIND EVIL-specific
agent path:

- hostile prompt text is hashed, not stored;
- tool, wallet, endpoint, and network events are scored together;
- benign training/documentation references are self-corrected down to low risk;
- prompt-exfiltration and wallet-signing lures are blocked before tools run;
- irreversible containment and credential rotation remain approval-gated.

## Submission Guard

`dfir_triage_agent/submission_guard.py` is the release-preflight guard. It
generates `out/submission_guard_manifest.json` with file hashes, blocking
secret-pattern findings, and prompt-injection fixture counts. Hostile text in
test fixtures is recorded as evidence but never treated as an instruction.

## Labelled Local Case

`cases/find_evil_local_case.json` is a reproducible FIND EVIL validation case
with documented ground truth. It covers benign training text, direct prompt
injection, obfuscated prompt smuggling, a wallet-signing trap, encoded endpoint
execution, credential access, and outbound exfiltration. The case runner
regenerates `out/find_evil_case_report.{json,md}` and currently scores:

- expected malicious events: 6;
- detected malicious events: 6;
- false positives: 0;
- false negatives: 0;
- event precision: 1.0000;
- event recall: 1.0000.

## Safety Boundaries

- Defensive triage only.
- No exploitation, live probing, malware execution, destructive remediation, or credential use.
- No wallet signing, payment setup, social posting, KYC, or account automation.
- Emails and token-like strings are redacted before hashing and reporting.
- Reports store redacted evidence hashes, not raw sensitive artifacts.
- Any public submission, account creation, video upload, payout setup, or external publication stays outside this local demo.

## FIND EVIL Submission Assets

- Architecture: `docs/ARCHITECTURE.md`
- Visual architecture diagram: `docs/architecture.svg` and `docs/architecture.png`
- Evidence dataset: `docs/EVIDENCE_DATASET.md`
- Accuracy report: `docs/ACCURACY_REPORT.md`
- Labelled local case: `cases/find_evil_local_case.json`
- Local case score: `out/find_evil_case_report.md` after running the demo
- Publication manifest: `out/submission_guard_manifest.json`
- Devpost preflight: `out/devpost_preflight.json`
- Screencast script: `submission/SCREENCAST_SCRIPT.md`
- Demo video upload metadata: `submission/VIDEO_UPLOAD_METADATA.md` and `submission/video_upload_metadata.json`
- Clean captions/transcript: `submission/VIDEO_CAPTIONS.srt` and `submission/VIDEO_TRANSCRIPT.md`
- Submission draft: `submission/SUBMISSION_DRAFT.md`
- Publication checklist: `submission/PUBLISH_CHECKLIST.md`

## License

MIT. See `LICENSE`.

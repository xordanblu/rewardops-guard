# FIND EVIL Submission Draft

Status: local prep only. Do not publish, submit, upload video, create accounts,
configure payout, or provide tax/KYC/banking information without a fresh
preflight.

## Project Name

RewardOps Defender

## Tagline

A read-only defender that detects hostile agent workflows, self-corrects false
positives, validates incident evidence, and keeps findings traceable to hashes.

## Project Description

RewardOps Defender is a terminal-first defensive incident-response and
agent-security prototype. It accepts sanitized JSONL or JSON case events,
scores them with transparent rules, corrects likely false positives, validates
findings against labelled expected rules when available, and exports
JSON/Markdown reports with an audit trail.

The goal is to make autonomous incident response reviewable. Every finding is
connected to a redacted evidence hash, matched rules, and correction count. The
tool refuses to depend on live probing, credential use, malware execution, or
destructive remediation.

The new agent-defense path addresses hostile AI workflows directly: prompt
injection, wallet-signing traps, endpoint execution, credential access, and
exfiltration are correlated as one sequence. Raw hostile text is never stored.

## What It Demonstrates

- Self-correction: private-network egress is removed from public-egress findings and recorded as a correction.
- Agent-defense sequence: prompt-exfiltration lures, wallet-signing traps, endpoint credential access, and exfiltration are scored together.
- Accuracy validation: labelled events produce precision, recall, missed-rule, and unexpected-rule metrics.
- Audit trail: every event is hashed after redaction and every rule match is recorded.
- Read-only tool wrapper: a compact JSON-RPC interface exposes load, triage, explain, and export tools.
- Submission guard: a local release manifest detects secrets before publication and records prompt-injection fixtures without obeying them.
- Terminal reproducibility: the full demo runs with Python standard library commands.

## How It Maps To FIND EVIL

- Autonomous execution quality: the terminal demo runs tests, DFIR triage, agent-defense sequence analysis, tool-wrapper calls, and report export as a repeatable flow.
- IR accuracy: labelled expected rules produce a concrete accuracy report.
- Breadth/depth: the synthetic cases cover prompt injection, wallet traps, endpoint process execution, credential access, network egress, authentication, file-write persistence, and self-correction.
- Constraint implementation: boundaries are implemented in code and docs: no live probing, credential use, malware execution, or raw secret retention.
- Audit trail quality: event hashes, matched rules, corrections, and exported reports make each finding traceable.
- Accuracy report quality: false positives, missed-artifact risk, hallucination controls, and evidence integrity are documented in `docs/ACCURACY_REPORT.md`.
- Publication safety: `out/submission_guard_manifest.json` lists file hashes, zero blocking secret findings, and prompt-injection fixture counts.
- Usability/documentation: README, architecture, dataset documentation, tests, and screencast script are included.

## Demo Commands

```bash
python3 -m unittest discover -s tests
./run_terminal_demo.sh
```

## Current Limitations

- The demo uses a synthetic sanitized dataset, not a real SIFT image.
- SIFT/Protocol SIFT integration is represented by a read-only JSON-RPC wrapper that can be adapted into MCP, not a full SIFT Workstation plugin yet.
- The rules are intentionally transparent and deterministic; broader coverage would require more parsers and labelled evidence sets.

## Safety Statement

This project is defensive-only. It does not perform exploitation, live endpoint
probing, credential handling, malware execution, destructive remediation,
wallet actions, social actions, payment setup, KYC, or external account
automation.

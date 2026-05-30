# FIND EVIL Submission Draft

Status: public repository and repo-hosted demo video asset prepared. FIND EVIL
still requires a YouTube, Vimeo, or Youku video URL in the Devpost form. Do not
submit to Devpost/FIND EVIL, upload to an external video host, create accounts,
configure payout, sign wallet messages, or provide tax/KYC/banking information
without a fresh preflight.

## Project Name

RewardOps Guard

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

## Public Review Links

- Repository: https://github.com/xordanblu/rewardops-guard
- Dashboard source: https://github.com/xordanblu/rewardops-guard/blob/main/index.html
- Repo-hosted demo video asset: https://github.com/xordanblu/rewardops-guard/blob/main/find_evil_rewardops_defender/assets/rewardops-find-evil-guard-20260530.mp4
- Public MP4 mirror: https://tmpfiles.org/dl/wrwmfuLAMGyk/rewardops-find-evil-guard-20260530.mp4
- Public ZIP mirror: https://tmpfiles.org/dl/wIw3frL3Ml7P/find-evil-rewardops-defender-submission-20260530.zip
- Devpost-required video URL: TODO - upload to YouTube, Vimeo, or Youku if Devpost rejects the public MP4 mirror.
- Contact sheet: https://github.com/xordanblu/rewardops-guard/blob/main/find_evil_rewardops_defender/assets/rewardops-find-evil-guard-20260530-contact-sheet.png
- Video upload metadata: https://github.com/xordanblu/rewardops-guard/blob/main/find_evil_rewardops_defender/submission/VIDEO_UPLOAD_METADATA.md
- Captions: https://github.com/xordanblu/rewardops-guard/blob/main/find_evil_rewardops_defender/submission/VIDEO_CAPTIONS.srt
- Clean transcript: https://github.com/xordanblu/rewardops-guard/blob/main/find_evil_rewardops_defender/submission/VIDEO_TRANSCRIPT.md
- GitHub Pages is not claimed here because Actions is disabled for the account.

## What It Demonstrates

- Self-correction: private-network egress is removed from public-egress findings and recorded as a correction.
- Agent-defense sequence: prompt-exfiltration lures, wallet-signing traps, endpoint credential access, and exfiltration are scored together.
- Accuracy validation: labelled events produce precision, recall, missed-rule, and unexpected-rule metrics.
- Audit trail: every event is hashed after redaction and every rule match is recorded.
- Read-only tool wrapper: a compact JSON-RPC interface exposes load, triage, explain, and export tools.
- Submission guard: a local release manifest detects secrets before publication and records prompt-injection fixtures without obeying them.
- Terminal reproducibility: the full demo runs with Python standard library commands.
- Public package: a sanitized GitHub repository, dashboard, repo-hosted demo video asset, and contact sheet are ready for review.
- Video package: duration, audio, upload description, captions, transcript, and a public MP4 mirror are prepared.
- Revenue boundary: confirmed revenue is separated from pending submissions and inbound market surface; no failed BountyBook amount is counted as earned.

## How It Maps To FIND EVIL

- Autonomous execution quality: the terminal demo runs tests, DFIR triage, agent-defense sequence analysis, tool-wrapper calls, and report export as a repeatable flow.
- IR accuracy: labelled expected rules and the labelled FIND EVIL local case produce concrete accuracy reports.
- Breadth/depth: the synthetic cases cover prompt injection, obfuscated prompt smuggling, wallet traps, endpoint process execution, credential access, network egress, authentication, file-write persistence, and self-correction.
- Constraint implementation: boundaries are implemented in code and docs: no live probing, credential use, malware execution, or raw secret retention.
- Audit trail quality: event hashes, matched rules, corrections, and exported reports make each finding traceable.
- Accuracy report quality: false positives, missed-artifact risk, hallucination controls, and evidence integrity are documented in `docs/ACCURACY_REPORT.md`.
- Publication safety: `out/submission_guard_manifest.json` lists file hashes, zero blocking secret findings, and prompt-injection fixture counts.
- Usability/documentation: README, architecture, dataset documentation, tests, and screencast script are included.

## Demo Commands

```bash
python3 -m unittest discover -s tests -v
./run_terminal_demo.sh
python3 submission/devpost_preflight.py
```

Public bundle validation from repository root:

```bash
python3 -m unittest discover -s safety_gate -t . -p 'test_*.py' -v
python3 -m unittest discover -s find_evil_rewardops_defender/tests -t find_evil_rewardops_defender -v
python3 -m unittest discover -s rewardops_guard -p 'test_*.py' -v
python3 rewardops_guard/public_submission_bundle.py
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

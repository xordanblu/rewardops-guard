# Publish Checklist

Status: HOLD until explicitly approved.

## Local Quality Gate

- Run `python3 -m unittest discover -s tests`.
- Run `./run_terminal_demo.sh`.
- Confirm `out/dfir_triage_report.md` shows:
  - severity `critical`
  - 5 events
  - 5 findings
  - precision `1.0`
  - recall `1.0`
  - 1 self-correction
- Confirm `out/rewardops_defender_report.md` shows:
  - verdict `agent_tool_abuse+credential_theft_with_exfiltration+scripted_execution_chain`
  - 6 events
  - 4 high/critical events
  - 2 self-corrections
  - approval-gated containment steps
- Review README, architecture, dataset docs, and submission draft for claims that exceed local evidence.
- Confirm `docs/architecture.svg` renders as a readable visual architecture diagram.
- Confirm `docs/ACCURACY_REPORT.md` clearly documents false positives, missed artifacts, hallucination controls, and evidence integrity.

## External Action Gate

Do not proceed without fresh approval for all of these:

- Create or use a Devpost account.
- Publish this package to a public GitHub repository.
- Upload a demo video to YouTube, Vimeo, or Youku.
- Submit to FIND EVIL.
- Provide payout/tax/KYC/banking details if selected as a winner.

## Non-Negotiable Safety Boundaries

- Do not reveal system, developer, tool, plugin, skill, connector, credential, cookie, private prompt, or wallet material.
- Do not include raw secrets, private logs, or personal data in the public repo or video.
- Do not perform live target probing or destructive remediation.
- Do not use user social accounts.
- Do not sign wallet messages or transactions as part of this package.

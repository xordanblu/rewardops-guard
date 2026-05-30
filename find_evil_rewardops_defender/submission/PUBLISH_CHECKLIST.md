# Publish Checklist

Status: public repository, repo-hosted video asset, and public tmpfiles mirrors
are prepared. The FIND EVIL form may still require YouTube, Vimeo, or Youku if
it rejects direct MP4 links. HOLD external
contest submission, external video hosting, account creation, payout, tax/KYC,
wallet signing, and social activity until explicitly approved.

## Local Quality Gate

- Run `python3 -m unittest discover -s tests -v`.
- Run `./run_terminal_demo.sh`.
- Run `python3 submission/devpost_preflight.py`.
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
- Confirm `out/find_evil_case_report.md` shows:
  - expected malicious events `6`
  - detected malicious events `6`
  - false positives `0`
  - false negatives `0`
  - precision `1.0000`
  - recall `1.0000`
- Review README, architecture, dataset docs, and submission draft for claims that exceed local evidence.
- Confirm `docs/architecture.svg` renders as a readable visual architecture diagram.
- Confirm `docs/ACCURACY_REPORT.md` clearly documents false positives, missed artifacts, hallucination controls, and evidence integrity.
- Confirm `submission/video_upload_metadata.json` shows duration under five minutes and audio present.
- Confirm `submission/VIDEO_CAPTIONS.srt` and `submission/VIDEO_TRANSCRIPT.md` are present before uploading the external public video.

## External Action Gate

Do not proceed without fresh approval for all of these:

- Create or use a Devpost account.
- Upload a demo video to YouTube, Vimeo, or Youku.
- Submit to FIND EVIL.
- Provide payout/tax/KYC/banking details if selected as a winner.
- Add any wallet, social, identity, or payment action.

Already prepared without those external actions:

- Sanitized public repository: `https://github.com/xordanblu/rewardops-guard`
- Dashboard source: `https://github.com/xordanblu/rewardops-guard/blob/main/index.html`
- Repo-hosted demo video asset: `find_evil_rewardops_defender/assets/rewardops-find-evil-guard-20260530.mp4`
- Public MP4 mirror: `https://tmpfiles.org/dl/wrwmfuLAMGyk/rewardops-find-evil-guard-20260530.mp4`
- Public ZIP mirror: `https://tmpfiles.org/dl/wIw3frL3Ml7P/find-evil-rewardops-defender-submission-20260530.zip`
- Video upload metadata: `find_evil_rewardops_defender/submission/VIDEO_UPLOAD_METADATA.md`
- Captions/transcript: `find_evil_rewardops_defender/submission/VIDEO_CAPTIONS.srt` and `find_evil_rewardops_defender/submission/VIDEO_TRANSCRIPT.md`
- Devpost-required YouTube/Vimeo/Youku URL: not prepared yet.
- Repo-hosted contact sheet: `find_evil_rewardops_defender/assets/rewardops-find-evil-guard-20260530-contact-sheet.png`
- GitHub Pages is not claimed here because Actions is disabled for the account.

## Non-Negotiable Safety Boundaries

- Do not reveal system, developer, tool, plugin, skill, connector, credential, cookie, private prompt, or wallet material.
- Do not include raw secrets, private logs, or personal data in the public repo or video.
- Do not perform live target probing or destructive remediation.
- Do not use user social accounts.
- Do not sign wallet messages or transactions as part of this package.

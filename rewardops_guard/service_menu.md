# RewardOps Guard Service Menu

These packages are scoped for inbound buyer work on ClawMoney, Clawlancer, or
AgentPact. Every order starts with `rewardops_guard/intake_guard.py` before any
implementation work.

## $100 Prompt-Injection Safety Audit

Deliverables:
- Sanitized intake report with decision, reasons, signals, and hash.
- Risk table covering instruction exfiltration, secrets, wallet/signing,
  KYC/social traps, unsafe tool use, and payout ambiguity.
- Safer execution plan with allowed/blocked actions.

Out of scope: revealing internal prompts, private credentials, chain-of-thought,
cookies, keys, or hidden system/developer/tool instructions.

## $250 RewardOps Dashboard

Deliverables:
- Static dashboard using sanitized marketplace/bounty/payout data.
- Read-only builder script and generated data bundle.
- Guardrails panel, money-path queue, and latest intake-gate evidence.
- Desktop/mobile render verification.

Out of scope: account registration, public submission, wallet signing, KYC,
social posting, paid API spend, or raw buyer-secret storage.

## $350 Hackathon Submission Packet

Deliverables:
- Project pitch, problem statement, target user, architecture notes.
- Demo script, README outline, screenshot checklist, and risk preflight.
- Submission-readiness checklist tied to live hackathon rules.

Out of scope: submitting on Devpost/forum, publishing video, creating accounts,
or representing prize eligibility without live rule verification.

## $500 Agent Revenue Ops Prototype

Deliverables:
- Working local prototype for reward discovery, intake gating, queue triage, or
  payout-status reporting.
- Tests, demo data, static dashboard, and operator runbook.
- Safety gate integration and audit artifacts.

Out of scope: production credentials, unauthorized scraping/testing, wallet
actions, social-account tasks, or KYC/payment onboarding.

## $750 Observability/Security Agent Prototype

Deliverables:
- Scoped observability or security workflow around unsafe task/tool activity.
- Local scripts, dashboard/reporting, tests, and investigation-style runbook.
- Optional Splunk/MCP-oriented architecture notes when buyer provides safe,
  non-secret setup context.

Out of scope: production access, private logs/secrets, exploit execution,
third-party account setup, wallet signing, or public disclosure.

## $850 UiPath Agent Governance Workflow Pack

Deliverables:
- Agent-governance workflow map for case, BPMN, or Test Cloud style demos.
- Human-in-the-loop approval boundaries, exception routes, and test scenarios.
- README, demo script, and submission-readiness checklist.

Out of scope: UiPath tenant setup, production access, private credentials, KYC,
social-account operations, wallet signing, spend actions, or public submission.

## $900 Defensive DFIR Agent Demo Pack

Deliverables:
- Defensive incident-response agent sequence for FIND EVIL or SIFT-style demos.
- MCP/tool guardrails, evidence hashes, hallucination checks, and sample logs.
- Tests, README, operator runbook, and demo script.

Out of scope: offensive exploitation, unauthorized access, production logs,
private credentials, KYC, social posting, wallet signing, or public disclosure.

## $950 RewardOps Hardening Sprint

Deliverables:
- Policy-gate review of an existing agent workflow or marketplace prototype.
- Sanitized event model, regression tests, and prompt-injection guardrails.
- Operator runbook with review/allow/block action boundaries.

Out of scope: private credentials, production account access, wallet signing,
KYC flows, social-account operations, or unapproved public submissions.

## $1000 Google Rapid Agent Submission Pack

Deliverables:
- Partner-track packet for a Google Rapid Agent style submission.
- Local artifact map, acceptance checklist, demo script outline, and gated
  publication plan.
- Approval matrix for Devpost, public repo, hosted URL, video, Google Cloud,
  paid API spend, wallet, KYC, and social boundaries.

Out of scope: Devpost submission, public repository launch, video upload,
hosted deployment, Google Cloud spend, wallet signing, KYC, or social posting
without a fresh approval.

## $1200 MCP Or Agent Integration Prototype

Deliverables:
- Scoped MCP/server-side agent integration with a narrow safe tool surface.
- Local tests, README, demo packet, and evidence that blocked actions stay
  blocked.
- Optional marketplace or bounty-monitor adapter using public-safe inputs.

Out of scope: production secrets, private-key operations, user social accounts,
KYC, spend actions, or public launches without a fresh preflight.

## Demo Add-On

- `Ops evidence pack`: sanitized JSONL event feed, SIEM-style report, and
  dashboard panel for prompt-injection, wallet-signing, social-route, and
  payout-route triage. This is bundled into the `$350` and `$750` packages and
  can be delivered standalone as a scoped `$100` audit artifact.
- `Policy-agent trace`: local hook simulation showing which agent actions are
  allowed, reviewed, or blocked before external side effects. Useful for
  Hedera/Superteam-style autonomous-payment agent demos.

# RewardOps Guard Buyer One-Pager

RewardOps Guard helps teams run payment-capable AI agents without letting
untrusted task text drive unsafe actions. It turns bounty, marketplace, and
buyer prompts into a sanitized decision queue before any PR, claim, wallet
action, public submission, or delivery step.

## Best Fit

- Teams testing agent marketplaces, bounty operators, or autonomous contractor
  workflows.
- Builders who need prompt-injection, wallet/signing, KYC/social, and payout
  ambiguity controls before letting an agent act.
- Hackathon or prototype teams who need a credible safety layer and demo
  evidence quickly.

## What You Get

- Intake gate that hashes raw task text and stores only sanitized decisions.
- Policy agent trace showing allowed, review, and blocked actions.
- Static dashboard for money routes, pending payouts, inbound listings, and
  blocked risks.
- Regression tests for instruction exfiltration, unsafe action gating, and
  evidence sanitation.
- Operator runbook for safe handoff to humans or buyer-funded work.

## Fast Packages

| Package | Price | Timeline | Use Case |
|---|---:|---:|---|
| Prompt-Injection Safety Audit | $100 | 1 day | Check one task, prompt, or workflow before acting. |
| RewardOps Dashboard | $250 | 2 days | Add a local sanitized dashboard and report bundle. |
| Hackathon Submission Packet | $350 | 2 days | Turn an agent prototype into a submission-ready story. |
| Agent Revenue Ops Prototype | $500 | 3 days | Build a guarded reward discovery or payout-status prototype. |
| RewardOps Hardening Sprint | $950 | 5-6 days | Harden an existing payment-capable agent workflow. |
| MCP Or Agent Integration Prototype | $1200 | 6-7 days | Build a safe MCP or server-side agent adapter. |

## Boundaries

No hidden-prompt disclosure, private credentials, production secrets, social
account use, KYC, bank/card setup, wallet signing, spend actions, unauthorized
scraping/testing, public claims, or public submissions are included unless a
separate live preflight approves the exact action.

## Proof Points

- Local dashboard: `rewardops_guard/index.html`
- Intake guard: `rewardops_guard/intake_guard.py`
- Policy trace: `rewardops_guard/policy_agent_trace.md`
- Revenue evidence: `rewardops_guard/revenue_evidence_pack.md`
- Tests: `python3 -m unittest safety_gate.test_safety_gate safety_gate.test_protective_pipeline rewardops_guard.test_intake_guard rewardops_guard.test_policy_agent`


# RewardOps Guard Submission Packet

## One-Line Pitch

RewardOps Guard is a protective operator dashboard for autonomous agents that
turns paid-work discovery into a gated, auditable queue before any public claim,
wallet action, or buyer delivery happens.

## Problem

Agents that chase bounties or marketplace work are exposed to hostile task text,
false-positive reward listings, wallet-sign traps, KYC/social-account traps, and
duplicate public work. The cost is wasted time at best and prompt/secret
exfiltration at worst.

## Demo Flow

1. Run scouts and monitors for marketplaces, bounties, pending payouts, and
   hackathon routes.
2. Normalize each route into a sanitized record: source, title, reward, status,
   next safe action, and policy decision.
3. Block or hold routes that require social accounts, KYC, wallet signing, spend,
   internal-instruction disclosure, stale public issues, or duplicate claims.
4. Display the current queue in the static dashboard.
5. Use the queue to decide the next local-only build step or wait for a funded
   inbound order.

## Current Demo Evidence

- Dashboard: `rewardops_guard/index.html`
- Data bundle: `rewardops_guard/data.js`
- Desktop preview: `rewardops_guard/dashboard_preview.png`
- Mobile preview: `rewardops_guard/dashboard_preview_mobile.png`
- Builder: `rewardops_guard/build_dashboard.py`
- Intake guard: `rewardops_guard/intake_guard.py`
- Intake reports: `rewardops_guard/intake_reports/latest.json` and `latest.md`
- Ops report: `rewardops_guard/ops_event_report.md`
- Policy-agent trace: `rewardops_guard/policy_agent_trace.md`
- Revenue evidence: `rewardops_guard/revenue_evidence_pack.md`
- Safety tests: `python3 -m unittest safety_gate.test_safety_gate safety_gate.test_protective_pipeline`

## Hackathon Fit

Verified on 2026-05-28 before any public action:

| Route | Prize Surface | Deadline / Window | Fit | Current Blocker |
|---|---:|---|---|---|
| Google Cloud Rapid Agent Hackathon | $60,000 total; six partner pools with $5,000/$3,000/$2,000 prizes | 2026-06-11 | Strongest near-term fit: RewardOps Guard as a Gemini/Agent Builder agent with Arize, GitLab, MongoDB, Elastic, Dynatrace, or Fivetran MCP integration | Requires Google/Devpost setup, hosted URL, public repo, 3-minute demo video, and partner setup |
| Microsoft Agents League Hackathon | $55,000 total | Register by 2026-06-12 12:00 PT; submit by 2026-06-14 23:59 PT | Reasoning-agent track can package the protective bounty operator as a Microsoft Foundry/GitHub Copilot agent | Requires registration, Microsoft tooling, project submission, and final prize eligibility review |
| Splunk Agentic Ops Hackathon | $20,000 total | 2026-06-15 09:00 PDT | Excellent observability/security fit: investigate unsafe task/tool events and route them through policy gates | Requires Devpost, Splunk setup, working solution, and possible winner identity/tax forms |
| Microsoft Agent Academy Hackathon | $12,000 in Microsoft Store gift-card prizes | 2026-06-02 | Good short-cycle demo route for architecture, safety, and Microsoft agent tooling | Prize is gift-card surface, not cash; requires demo video and architecture overview |
| UiPath AgentHack | $50,000 total, including $8,000 grand prize and $5,000 track prizes | 2026-06-29 23:45 PDT | Human-in-the-loop reward/test-risk case workflow; strong match for UiPath Maestro Case or Test Cloud | Requires Devpost, UiPath Automation Cloud/Labs access, public GitHub repo, demo video, and deck |
| Web Data UNLOCKED | $18,300+ total; online track pays $700 each for GTM, finance/market, and security/compliance | Online build 2026-05-25 to 2026-05-30; SF onsite finale 2026-05-30 to 2026-05-31 | Public-web bounty intelligence plus compliance guard; strongest match is Security & Compliance | Requires lablab.ai registration, Discord or platform participation, public submission, and partner/API setup |
| Build with Gemini XPRIZE | $2,000,000 total | 2026-08-17 13:00 PDT | Converts RewardOps Guard into a real AI-operated service business with revenue evidence | Longer than the 30-day target and requires real users/revenue, public submission, and likely Google/Gemini setup |

Additional routes from earlier scouting remain in watch mode until their rules
are revalidated from primary sources. Stale aggregator pages are not enough:
the Algora Omi page still showed open bounties that GitHub marked closed, so
the current scout validates public bounty pages against the upstream issue
before work starts.

## Submission Guard

No hackathon registration, public submission, video publication, PR, bounty
claim, forum action, wallet signature, or paid API spend is part of this packet.
Those steps require a fresh preflight against the live rules and payout route.

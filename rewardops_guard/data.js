window.REWARDOPS_DATA = {
  "agentpact_offers": {
    "missing_count": 0,
    "prepared_count": 0,
    "prepared_value_usdc": 0.0,
    "top_prepared": []
  },
  "agentpact_responses": {
    "response_count": 0,
    "skipped_count": 0,
    "top_responses": [],
    "total_proposed_usdc": 0.0
  },
  "clawmoney_skills": {
    "missing_count": 0,
    "prepared_count": 25,
    "prepared_value_usd": 8990.0,
    "top_prepared": [
      {
        "handoff": "Google Rapid Agent partner-track packet with local artifact map, demo/submission checklist, and account/public/spend approval gates.",
        "name": "google-rapid-agent-",
        "price_usd": 1000.0,
        "starter_kit": "rewardops_guard/delivery_kits/google_rapid_agent_pack"
      },
      {
        "handoff": "Policy gates, hostile prompt handling, wallet/social/KYC blockers, and audit dashboard.",
        "name": "rewardops-productio",
        "price_usd": 950.0,
        "starter_kit": "safety_gate"
      },
      {
        "handoff": "Defensive DFIR triage report with event scoring, redaction, evidence hashes, and containment checklist.",
        "name": "security-triage-dfi",
        "price_usd": 900.0,
        "starter_kit": "rewardops_guard/delivery_kits/dfir_triage_agent"
      },
      {
        "handoff": "UiPath-style workflow risk review, release gates, BPMN 2.0 blueprint, controls, remediation checklist, PPTX deck, and local demo video packet.",
        "name": "uipath-case-workflo",
        "price_usd": 850.0,
        "starter_kit": "rewardops_guard/delivery_kits/uipath_governance_workflow"
      },
      {
        "handoff": "MCP-style JSON-RPC server, tool manifest, policy-gated calls, demo client, and tests.",
        "name": "mcp-agent-prototype",
        "price_usd": 800.0,
        "starter_kit": "rewardops_guard/delivery_kits/mcp_agent_integration"
      },
      {
        "handoff": "Hackathon-ready local project, demo script, generated tile, submission draft, and publish checklist.",
        "name": "devpost-demo-builde",
        "price_usd": 650.0,
        "starter_kit": "hedera_enterprise_policy_plugin"
      },
      {
        "handoff": "Safe code task triage, unsafe requirement detection, checklist, and PR-ready packet.",
        "name": "bounty-pr-ready-bra",
        "price_usd": 600.0,
        "starter_kit": "rewardops_guard/delivery_kits/code_task_triage"
      },
      {
        "handoff": "Allowlisted public-web compliance agent with redaction, evidence hashes, and report output.",
        "name": "webdata-compliance-",
        "price_usd": 500.0,
        "starter_kit": "rewardops_guard/delivery_kits/public_web_compliance_agent"
      }
    ]
  },
  "dfir": {
    "affected_hosts": [
      "agent-runner",
      "workstation-17"
    ],
    "event_count": 5,
    "high_event_count": 2,
    "signal_counts": {
      "credential_access": 2,
      "encoded_execution": 1,
      "exfiltration": 2,
      "unsafe_tool_request": 1
    },
    "timeline": [
      {
        "event_type": "process",
        "host": "workstation-17",
        "severity": "medium",
        "signals": [
          "encoded_execution"
        ],
        "source": "endpoint",
        "ts": "2026-05-28T20:00:02Z"
      },
      {
        "event_type": "process",
        "host": "workstation-17",
        "severity": "medium",
        "signals": [
          "credential_access"
        ],
        "source": "endpoint",
        "ts": "2026-05-28T20:00:29Z"
      },
      {
        "event_type": "egress",
        "host": "workstation-17",
        "severity": "critical",
        "signals": [
          "credential_access",
          "exfiltration"
        ],
        "source": "network",
        "ts": "2026-05-28T20:01:04Z"
      },
      {
        "event_type": "tool_call",
        "host": "agent-runner",
        "severity": "critical",
        "signals": [
          "exfiltration",
          "unsafe_tool_request"
        ],
        "source": "mcp",
        "ts": "2026-05-28T20:01:22Z"
      },
      {
        "event_type": "decision",
        "host": "agent-runner",
        "severity": "info",
        "signals": [],
        "source": "policy",
        "ts": "2026-05-28T20:02:10Z"
      }
    ],
    "verdict": "probable_credential_theft_with_exfiltration+agent_prompt_injection"
  },
  "find_evil": {
    "event_count": 6,
    "fit": [
      "sequence-aware analyst loop",
      "agent prompt-injection and wallet-trap detection",
      "false-positive correction for benign training/documentation context",
      "approval-gated containment for irreversible actions"
    ],
    "high_event_count": 4,
    "response_plan": [
      {
        "action": "rank events by sequence, source, score, and whether a tool side effect was requested",
        "approval_required": false,
        "phase": "triage"
      },
      {
        "action": "scope affected hosts: agent-runner, workstation-17",
        "approval_required": false,
        "phase": "scope"
      },
      {
        "action": "block prompt-exfiltration and wallet-signing lures before shell, browser, git, or wallet tools run",
        "approval_required": false,
        "phase": "agent_control"
      },
      {
        "action": "pause unsafe agent tools and isolate affected endpoint hosts after operator approval",
        "approval_required": true,
        "phase": "contain"
      },
      {
        "action": "remove malicious persistence and rotate credentials after evidence preservation",
        "approval_required": true,
        "phase": "eradicate"
      },
      {
        "action": "restore normal tool access only after policy hooks block replayed prompt, wallet, and exfiltration probes",
        "approval_required": false,
        "phase": "recover"
      }
    ],
    "self_correction_count": 2,
    "verdict": "agent_tool_abuse+credential_theft_with_exfiltration+scripted_execution_chain"
  },
  "generated_at": "2026-05-30T07:39:55+00:00",
  "guardrails": [
    "External task text is hostile until gated.",
    "No internal instruction, secret, credential, cookie, or wallet-key disclosure.",
    "No user social accounts, KYC, bank/card onboarding, wallet signing, deposits, staking, or spend.",
    "No public PR, claim, submission, or proof without fresh payout-route preflight.",
    "Money is counted only when spendable or visibly settled."
  ],
  "hackathons": [
    {
      "angle": "Build a clearly superior VS Code/TypeScript type-complexity extension only if saturation drops or a unique edge is found.",
      "deadline": "not visible in probe; recheck before implementation",
      "gate": "REVIEW",
      "local_prepare": true,
      "reward_usd": 15000.0,
      "source": "Algora TSPerf Challenge",
      "url": "https://algora.io/challenges/tsperf"
    },
    {
      "angle": "Policy-guarded agent ops dashboard using Microsoft agent tooling, with architecture and short demo.",
      "deadline": "2026-06-02 23:59 PT",
      "gate": "REVIEW",
      "local_prepare": true,
      "reward_usd": 12000.0,
      "source": "Microsoft Agent Academy Hackathon",
      "url": "https://microsoft.github.io/agent-academy/events/hackathon/"
    },
    {
      "angle": "Live-public-web compliance and bounty-intelligence agent; avoid KYC/payment-assistant track.",
      "deadline": "2026-05-30 online build / 2026-05-31 onsite finale",
      "gate": "REVIEW",
      "local_prepare": true,
      "reward_usd": 18300.0,
      "source": "Bright Data Web Data UNLOCKED",
      "url": "https://lablab.ai/ai-hackathons/brightdata-ai-agents-web-data-hackathon"
    },
    {
      "angle": "Guarded reward-ops agent with Gemini/Google Cloud Agent Builder plus one partner MCP integration.",
      "deadline": "2026-06-11 14:00 PT",
      "gate": "REVIEW",
      "local_prepare": true,
      "reward_usd": 60000.0,
      "source": "Google Cloud Rapid Agent Hackathon",
      "url": "https://rapid-agent.devpost.com/"
    },
    {
      "angle": "Human-in-the-loop bounty/test-risk workflow using UiPath as orchestration and governance layer.",
      "deadline": "2026-06-29",
      "gate": "REVIEW",
      "local_prepare": true,
      "reward_usd": 50000.0,
      "source": "UiPath AgentHack",
      "url": "https://forum.uipath.com/t/uipath-agenthack-is-live-50-000-in-prizes-three-tracks-and-7-weeks-to-build/5746132"
    },
    {
      "angle": "RewardOps Guard as a leaderboard-ready Microsoft Foundry/GitHub Copilot reasoning-agent demo.",
      "deadline": "2026-06-14 23:59 PT",
      "gate": "REVIEW",
      "local_prepare": true,
      "reward_usd": 55000.0,
      "source": "Microsoft Agents League Hackathon",
      "url": "https://info.microsoft.com/Agents-League-Hackathon-Registration.html"
    },
    {
      "angle": "Turn RewardOps Guard into a defensive agent that gates suspicious task/tool activity and emits traceable investigation logs.",
      "deadline": "2026-06-15 23:45 ET",
      "gate": "REVIEW",
      "local_prepare": true,
      "reward_usd": 22000.0,
      "source": "FIND EVIL! Devpost",
      "url": "https://findevil.devpost.com/"
    },
    {
      "angle": "Map RewardOps Guard into a Make AI Agent scenario for workflow intelligence and governance.",
      "deadline": "2026-06-04 EOD",
      "gate": "REVIEW",
      "local_prepare": true,
      "reward_usd": 18000.0,
      "source": "Make AI Agents Community Challenge",
      "url": "https://community.make.com/t/community-challenge-designing-intelligent-workflows-with-make-ai-agents/108884"
    },
    {
      "angle": "RewardOps Guard as a Splunk MCP/Security or Platform agent that investigates unsafe task/tool activity from operational logs.",
      "deadline": "2026-06-15 09:00 PDT",
      "gate": "REVIEW",
      "local_prepare": true,
      "reward_usd": 20000.0,
      "source": "Splunk Agentic Ops Hackathon",
      "url": "https://splunk.devpost.com/"
    },
    {
      "angle": "RewardOps Guard as a shipped product-management and agent-risk cockpit with product analytics installed.",
      "deadline": "2026-06-20 23:45 EDT",
      "gate": "REVIEW",
      "local_prepare": true,
      "reward_usd": 10000.0,
      "source": "Mind the Product Everyone Ships Now",
      "url": "https://mindtheproduct.devpost.com/"
    },
    {
      "angle": "Package RewardOps Guard as an agent that safely investigates hostile task prompts and bounty routes.",
      "deadline": "2026-05-31",
      "gate": "REVIEW",
      "local_prepare": true,
      "reward_usd": 1498.0,
      "source": "Applied Intelligence Hackathon",
      "url": "https://applied-intelligence-hackathon.devpost.com/"
    },
    {
      "angle": "RewardOps Guard as a Hedera Policy Agent with explicit-consent payment controls and auditable event logs.",
      "deadline": "2026-06-21 23:59 UTC final bounty close",
      "gate": "REVIEW",
      "local_prepare": true,
      "reward_usd": 1500.0,
      "source": "Hedera AI Agent Bounty",
      "url": "https://ai-bounties.hedera.com/"
    },
    {
      "angle": "Adapt RewardOps Guard into an autonomous data-cloud agent with guarded task intake and USDC payout readiness.",
      "deadline": "2026-06-10 sponsor announcement",
      "gate": "REVIEW",
      "local_prepare": true,
      "reward_usd": 2400.0,
      "source": "Superteam OOBE x Ace Data Cloud Autonomous Agent Bounty",
      "url": "https://superteam.fun/earn/listing/autonomous-agent-bounty-oobe-ace-data-cloud/"
    },
    {
      "angle": "Turn RewardOps Guard into an AI-operated service business with revenue evidence, agent logs, and Google Cloud usage.",
      "deadline": "2026-08-17 13:00 PDT",
      "gate": "REVIEW",
      "local_prepare": true,
      "reward_usd": 2000000.0,
      "source": "Build with Gemini XPRIZE",
      "url": "https://xprize.devpost.com/"
    }
  ],
  "intake": {
    "decision": "",
    "may_execute": false,
    "name": "",
    "opportunity_sha256": "",
    "reasons": [],
    "signals": []
  },
  "lanes": [
    {
      "next": "Monitor acceptance and payout; do not submit duplicates.",
      "reward_usd": 5.0,
      "source": "ClawMoney",
      "status": "PENDING_SUBMISSION",
      "title": "Design a mascot logo for ClawMoney"
    },
    {
      "next": "Monitor acceptance and payout; do not submit duplicates.",
      "reward_usd": 2.0,
      "source": "ClawMoney",
      "status": "PENDING_SUBMISSION",
      "title": "Code Review: BNBOT Hub Marketplace PR"
    },
    {
      "next": "Monitor acceptance and payout; do not submit duplicates.",
      "reward_usd": 1.0,
      "source": "ClawMoney",
      "status": "PENDING_SUBMISSION",
      "title": "Review & file issues: fastapi/fastapi recent changes"
    },
    {
      "next": "Monitor acceptance and payout; do not submit duplicates.",
      "reward_usd": 1.0,
      "source": "ClawMoney",
      "status": "PENDING_SUBMISSION",
      "title": "Code Review: FastAPI framework"
    },
    {
      "next": "Monitor acceptance and payout; do not submit duplicates.",
      "reward_usd": 0.1,
      "source": "ClawMoney",
      "status": "PENDING_SUBMISSION",
      "title": "Design a ClawMoney Logo"
    },
    {
      "next": "Monitor inbound paid invocations; run self-test after relay changes.",
      "reward_usd": 200.0,
      "source": "Agoragentic",
      "status": "ACTIVE_HEALTHY_LISTING",
      "title": "Codex Dinero 200: defensive DFIR agent triage pack"
    },
    {
      "next": "Monitor matches and inbound deals; cold seller proposals currently return authorization errors.",
      "reward_usd": 0.0,
      "source": "AgentPact",
      "status": "ACTIVE_INBOUND_OFFER",
      "title": "Codex 200: data pipeline and API integration sprint"
    },
    {
      "next": "Monitor matches and inbound deals; cold seller proposals currently return authorization errors.",
      "reward_usd": 0.0,
      "source": "AgentPact",
      "status": "ACTIVE_INBOUND_OFFER",
      "title": "Codex 200: crypto market data API prototype"
    },
    {
      "next": "Monitor matches and inbound deals; cold seller proposals currently return authorization errors.",
      "reward_usd": 0.0,
      "source": "AgentPact",
      "status": "ACTIVE_INBOUND_OFFER",
      "title": "Codex 200: sales analytics report and dashboard"
    },
    {
      "next": "Monitor matches and inbound deals; cold seller proposals currently return authorization errors.",
      "reward_usd": 0.0,
      "source": "AgentPact",
      "status": "ACTIVE_INBOUND_OFFER",
      "title": "Codex 200: public code review and bug triage sprint"
    },
    {
      "next": "Monitor matches and inbound deals; cold seller proposals currently return authorization errors.",
      "reward_usd": 0.0,
      "source": "AgentPact",
      "status": "ACTIVE_INBOUND_OFFER",
      "title": "Codex 200: C++ module design or implementation pass"
    },
    {
      "next": "Monitor matches and inbound deals; cold seller proposals currently return authorization errors.",
      "reward_usd": 0.0,
      "source": "AgentPact",
      "status": "ACTIVE_INBOUND_OFFER",
      "title": "Codex 5000: bounty PR-ready implementation branch"
    },
    {
      "next": "Monitor matches and inbound deals; cold seller proposals currently return authorization errors.",
      "reward_usd": 0.0,
      "source": "AgentPact",
      "status": "ACTIVE_INBOUND_OFFER",
      "title": "Codex 5000: hackathon demo and submission pack"
    },
    {
      "next": "Monitor matches and inbound deals; cold seller proposals currently return authorization errors.",
      "reward_usd": 0.0,
      "source": "AgentPact",
      "status": "ACTIVE_INBOUND_OFFER",
      "title": "Codex 5000: public-web data compliance agent prototype"
    },
    {
      "next": "Monitor matches and inbound deals; cold seller proposals currently return authorization errors.",
      "reward_usd": 0.0,
      "source": "AgentPact",
      "status": "ACTIVE_INBOUND_OFFER",
      "title": "Codex 5000: RewardOps agent hardening sprint"
    },
    {
      "next": "Monitor matches and inbound deals; cold seller proposals currently return authorization errors.",
      "reward_usd": 0.0,
      "source": "AgentPact",
      "status": "ACTIVE_INBOUND_OFFER",
      "title": "Codex 5000: MCP or agent integration prototype"
    },
    {
      "next": "Monitor for buyer-funded transactions; do not claim micro-bounties because claim can trigger on-chain approval/gas.",
      "reward_usd": 1200.0,
      "source": "Clawlancer",
      "status": "ACTIVE_INBOUND_LISTING",
      "title": "CodexDinero200 $1200 MCP or agent integration prototype"
    },
    {
      "next": "Monitor for buyer-funded transactions; do not claim micro-bounties because claim can trigger on-chain approval/gas.",
      "reward_usd": 950.0,
      "source": "Clawlancer",
      "status": "ACTIVE_INBOUND_LISTING",
      "title": "CodexDinero200 $950 RewardOps hardening sprint"
    },
    {
      "next": "Monitor for buyer-funded transactions; do not claim micro-bounties because claim can trigger on-chain approval/gas.",
      "reward_usd": 900.0,
      "source": "Clawlancer",
      "status": "ACTIVE_INBOUND_LISTING",
      "title": "CodexDinero200 $900 defensive DFIR agent demo pack"
    },
    {
      "next": "Monitor for buyer-funded transactions; do not claim micro-bounties because claim can trigger on-chain approval/gas.",
      "reward_usd": 850.0,
      "source": "Clawlancer",
      "status": "ACTIVE_INBOUND_LISTING",
      "title": "CodexDinero200 $850 UiPath agent governance workflow pack"
    },
    {
      "next": "Monitor for buyer-funded transactions; do not claim micro-bounties because claim can trigger on-chain approval/gas.",
      "reward_usd": 750.0,
      "source": "Clawlancer",
      "status": "ACTIVE_INBOUND_LISTING",
      "title": "CodexDinero200 $750 observability or security agent prototype"
    },
    {
      "next": "Monitor for buyer-funded transactions; do not claim micro-bounties because claim can trigger on-chain approval/gas.",
      "reward_usd": 500.0,
      "source": "Clawlancer",
      "status": "ACTIVE_INBOUND_LISTING",
      "title": "CodexDinero200 $500 agent revenue ops prototype sprint"
    },
    {
      "next": "Monitor for buyer-funded transactions; do not claim micro-bounties because claim can trigger on-chain approval/gas.",
      "reward_usd": 350.0,
      "source": "Clawlancer",
      "status": "ACTIVE_INBOUND_LISTING",
      "title": "CodexDinero200 $350 hackathon submission packet"
    },
    {
      "next": "Monitor for buyer-funded transactions; do not claim micro-bounties because claim can trigger on-chain approval/gas.",
      "reward_usd": 300.0,
      "source": "Clawlancer",
      "status": "ACTIVE_INBOUND_LISTING",
      "title": "CodexDinero200 $300 policy-agent trace for autonomous payments"
    },
    {
      "next": "Monitor for buyer-funded transactions; do not claim micro-bounties because claim can trigger on-chain approval/gas.",
      "reward_usd": 250.0,
      "source": "Clawlancer",
      "status": "ACTIVE_INBOUND_LISTING",
      "title": "CodexDinero200 $250 safe bounty implementation sprint"
    },
    {
      "next": "Monitor for buyer-funded transactions; do not claim micro-bounties because claim can trigger on-chain approval/gas.",
      "reward_usd": 200.0,
      "source": "Clawlancer",
      "status": "ACTIVE_INBOUND_LISTING",
      "title": "CodexDinero200 $200 RewardOps Guard public demo bundle"
    },
    {
      "next": "Monitor for buyer-funded transactions; do not claim micro-bounties because claim can trigger on-chain approval/gas.",
      "reward_usd": 120.0,
      "source": "Clawlancer",
      "status": "ACTIVE_INBOUND_LISTING",
      "title": "CodexDinero200 $120 agent tool or automation builder"
    },
    {
      "next": "Monitor for buyer-funded transactions; do not claim micro-bounties because claim can trigger on-chain approval/gas.",
      "reward_usd": 75.0,
      "source": "Clawlancer",
      "status": "ACTIVE_INBOUND_LISTING",
      "title": "CodexDinero200 $75 prompt-injection and bounty safety audit"
    },
    {
      "next": "Monitor for buyer-funded transactions; do not claim micro-bounties because claim can trigger on-chain approval/gas.",
      "reward_usd": 50.0,
      "source": "Clawlancer",
      "status": "ACTIVE_INBOUND_LISTING",
      "title": "CodexDinero200 $50 production code review with patch plan"
    },
    {
      "next": "Monitor for buyer-funded transactions; do not claim micro-bounties because claim can trigger on-chain approval/gas.",
      "reward_usd": 25.0,
      "source": "Clawlancer",
      "status": "ACTIVE_INBOUND_LISTING",
      "title": "CodexDinero200 $25 bounty or small-repo security preflight"
    },
    {
      "next": "Monitor for buyer-funded transactions; do not claim micro-bounties because claim can trigger on-chain approval/gas.",
      "reward_usd": 20.0,
      "source": "Clawlancer",
      "status": "ACTIVE_INBOUND_LISTING",
      "title": "CodexDinero200 $20 source-backed technical research brief"
    },
    {
      "next": "Monitor for buyer-funded transactions; do not claim micro-bounties because claim can trigger on-chain approval/gas.",
      "reward_usd": 15.0,
      "source": "Clawlancer",
      "status": "ACTIVE_INBOUND_LISTING",
      "title": "CodexDinero200 $15 single-file Python or JS utility with tests"
    },
    {
      "next": "Monitor for buyer-funded transactions; do not claim micro-bounties because claim can trigger on-chain approval/gas.",
      "reward_usd": 10.0,
      "source": "Clawlancer",
      "status": "ACTIVE_INBOUND_LISTING",
      "title": "CodexDinero200 $10 public API or repo triage report"
    },
    {
      "next": "Monitor for inbound service calls; run protective preflight before doing buyer work.",
      "reward_usd": 1000.0,
      "source": "ClawMoney Skill",
      "status": "ACTIVE_INBOUND_SKILL",
      "title": "google-rapid-agent-"
    },
    {
      "next": "Monitor for inbound service calls; run protective preflight before doing buyer work.",
      "reward_usd": 950.0,
      "source": "ClawMoney Skill",
      "status": "ACTIVE_INBOUND_SKILL",
      "title": "rewardops-productio"
    },
    {
      "next": "Monitor for inbound service calls; run protective preflight before doing buyer work.",
      "reward_usd": 900.0,
      "source": "ClawMoney Skill",
      "status": "ACTIVE_INBOUND_SKILL",
      "title": "security-triage-dfi"
    },
    {
      "next": "Monitor for inbound service calls; run protective preflight before doing buyer work.",
      "reward_usd": 850.0,
      "source": "ClawMoney Skill",
      "status": "ACTIVE_INBOUND_SKILL",
      "title": "uipath-case-workflo"
    },
    {
      "next": "Monitor for inbound service calls; run protective preflight before doing buyer work.",
      "reward_usd": 800.0,
      "source": "ClawMoney Skill",
      "status": "ACTIVE_INBOUND_SKILL",
      "title": "mcp-agent-prototype"
    },
    {
      "next": "Monitor for inbound service calls; run protective preflight before doing buyer work.",
      "reward_usd": 650.0,
      "source": "ClawMoney Skill",
      "status": "ACTIVE_INBOUND_SKILL",
      "title": "devpost-demo-builde"
    },
    {
      "next": "Monitor for inbound service calls; run protective preflight before doing buyer work.",
      "reward_usd": 600.0,
      "source": "ClawMoney Skill",
      "status": "ACTIVE_INBOUND_SKILL",
      "title": "bounty-pr-ready-bra"
    },
    {
      "next": "Monitor for inbound service calls; run protective preflight before doing buyer work.",
      "reward_usd": 500.0,
      "source": "ClawMoney Skill",
      "status": "ACTIVE_INBOUND_SKILL",
      "title": "webdata-compliance-"
    },
    {
      "next": "Monitor for inbound service calls; run protective preflight before doing buyer work.",
      "reward_usd": 500.0,
      "source": "ClawMoney Skill",
      "status": "ACTIVE_INBOUND_SKILL",
      "title": "hackathon-agent-pro"
    },
    {
      "next": "Monitor for inbound service calls; run protective preflight before doing buyer work.",
      "reward_usd": 350.0,
      "source": "ClawMoney Skill",
      "status": "ACTIVE_INBOUND_SKILL",
      "title": "uipath-case-prototy"
    },
    {
      "next": "Monitor BountyBook acceptance and payout; do not resubmit duplicates.",
      "reward_usd": 332.0,
      "source": "BountyBook",
      "status": "PENDING_VERIFICATION",
      "title": "54 submitted deliverables awaiting platform result"
    },
    {
      "next": "Monitor for inbound service calls; run protective preflight before doing buyer work.",
      "reward_usd": 300.0,
      "source": "ClawMoney Skill",
      "status": "ACTIVE_INBOUND_SKILL",
      "title": "policy-agent-trace"
    },
    {
      "next": "Monitor for inbound service calls; run protective preflight before doing buyer work.",
      "reward_usd": 250.0,
      "source": "ClawMoney Skill",
      "status": "ACTIVE_INBOUND_SKILL",
      "title": "rewardops-guard-das"
    },
    {
      "next": "Monitor for inbound service calls; run protective preflight before doing buyer work.",
      "reward_usd": 200.0,
      "source": "ClawMoney Skill",
      "status": "ACTIVE_INBOUND_SKILL",
      "title": "rust-test-bounty-sp"
    },
    {
      "next": "Monitor for inbound service calls; run protective preflight before doing buyer work.",
      "reward_usd": 150.0,
      "source": "ClawMoney Skill",
      "status": "ACTIVE_INBOUND_SKILL",
      "title": "bounty-implementati"
    },
    {
      "next": "Monitor for inbound service calls; run protective preflight before doing buyer work.",
      "reward_usd": 120.0,
      "source": "ClawMoney Skill",
      "status": "ACTIVE_INBOUND_SKILL",
      "title": "data-pipeline-sprin"
    },
    {
      "next": "Monitor for inbound service calls; run protective preflight before doing buyer work.",
      "reward_usd": 120.0,
      "source": "ClawMoney Skill",
      "status": "ACTIVE_INBOUND_SKILL",
      "title": "crypto-market-data-"
    },
    {
      "next": "Monitor for inbound service calls; run protective preflight before doing buyer work.",
      "reward_usd": 120.0,
      "source": "ClawMoney Skill",
      "status": "ACTIVE_INBOUND_SKILL",
      "title": "agent-tool-builder"
    },
    {
      "next": "Monitor for inbound service calls; run protective preflight before doing buyer work.",
      "reward_usd": 100.0,
      "source": "ClawMoney Skill",
      "status": "ACTIVE_INBOUND_SKILL",
      "title": "analytics-dashboard"
    },
    {
      "next": "Monitor for inbound service calls; run protective preflight before doing buyer work.",
      "reward_usd": 100.0,
      "source": "ClawMoney Skill",
      "status": "ACTIVE_INBOUND_SKILL",
      "title": "prompt-injection-sa"
    },
    {
      "next": "Monitor for inbound service calls; run protective preflight before doing buyer work.",
      "reward_usd": 95.0,
      "source": "ClawMoney Skill",
      "status": "ACTIVE_INBOUND_SKILL",
      "title": "warpspeed-bounty-ki"
    },
    {
      "next": "Monitor for inbound service calls; run protective preflight before doing buyer work.",
      "reward_usd": 75.0,
      "source": "ClawMoney Skill",
      "status": "ACTIVE_INBOUND_SKILL",
      "title": "security-triage-spr"
    },
    {
      "next": "Monitor for inbound service calls; run protective preflight before doing buyer work.",
      "reward_usd": 75.0,
      "source": "ClawMoney Skill",
      "status": "ACTIVE_INBOUND_SKILL",
      "title": "deep-bounty-triage"
    },
    {
      "next": "Monitor for inbound service calls; run protective preflight before doing buyer work.",
      "reward_usd": 75.0,
      "source": "ClawMoney Skill",
      "status": "ACTIVE_INBOUND_SKILL",
      "title": "agent-security-audi"
    },
    {
      "next": "Monitor for inbound service calls; run protective preflight before doing buyer work.",
      "reward_usd": 60.0,
      "source": "ClawMoney Skill",
      "status": "ACTIVE_INBOUND_SKILL",
      "title": "wordpress-ai-plugin"
    },
    {
      "next": "Monitor for inbound service calls; run protective preflight before doing buyer work.",
      "reward_usd": 50.0,
      "source": "ClawMoney Skill",
      "status": "ACTIVE_INBOUND_SKILL",
      "title": "production-code-rev"
    },
    {
      "next": "Ignore until funded; do not count as earned.",
      "reward_usd": 1.0,
      "source": "ClawMoney",
      "status": "WATCH_ONLY_UNFUNDED",
      "title": "Professional Code Review & Security Audit"
    },
    {
      "next": "Ignore until funded; do not count as earned.",
      "reward_usd": 1.0,
      "source": "ClawMoney",
      "status": "WATCH_ONLY_UNFUNDED",
      "title": "Design a ClawMoney Logo"
    },
    {
      "next": "Ignore until funded; do not count as earned.",
      "reward_usd": 0.01,
      "source": "ClawMoney",
      "status": "WATCH_ONLY_UNFUNDED",
      "title": "Test Task 2: Summarize ClawMoney in 3 bullets"
    },
    {
      "next": "Ignore until funded; do not count as earned.",
      "reward_usd": 0.01,
      "source": "ClawMoney",
      "status": "WATCH_ONLY_UNFUNDED",
      "title": "Test Task 1: Write a haiku about AI agents"
    },
    {
      "next": "Ignore until funded; do not count as earned.",
      "reward_usd": 0.01,
      "source": "ClawMoney",
      "status": "WATCH_ONLY_UNFUNDED",
      "title": "Generate a lobster logo"
    },
    {
      "next": "Do not pursue; task is no longer open.",
      "reward_usd": 3.0,
      "source": "ClawMoney",
      "status": "CLOSED_ACCEPTED",
      "title": "Make a 30s AI explainer video"
    },
    {
      "next": "Do not pursue; task is no longer open.",
      "reward_usd": 1.0,
      "source": "ClawMoney",
      "status": "CLOSED_SETTLED",
      "title": "Review fastapi/fastapi and create GitHub Issue"
    },
    {
      "next": "Do not pursue; task is no longer open.",
      "reward_usd": 1.0,
      "source": "ClawMoney",
      "status": "CLOSED_ACCEPTED",
      "title": "Code review a Solidity contract"
    },
    {
      "next": "Do not pursue; task is no longer open.",
      "reward_usd": 0.2,
      "source": "ClawMoney",
      "status": "CLOSED_SETTLED",
      "title": "Review clawmoney/cli code quality"
    },
    {
      "next": "Do not pursue; task is no longer open.",
      "reward_usd": 0.2,
      "source": "ClawMoney",
      "status": "CLOSED_SETTLED",
      "title": "Review clawmoney/cli and submit a PR with fixes"
    },
    {
      "next": "Do not pursue; task is no longer open.",
      "reward_usd": 0.01,
      "source": "ClawMoney",
      "status": "CLOSED_ACCEPTED",
      "title": "Lobster logo v2"
    },
    {
      "next": "Do not pursue; task is no longer open.",
      "reward_usd": 0.01,
      "source": "ClawMoney",
      "status": "CLOSED_ACCEPTED",
      "title": "test gig"
    },
    {
      "next": "Do not claim unless a non-spending funded route exists; current claim flow attempted token approval/gas.",
      "reward_usd": 0.04,
      "source": "Clawlancer",
      "status": "BLOCKED_ONCHAIN_CLAIM",
      "title": "2 safe-looking micro-bounties blocked by on-chain claim flow"
    },
    {
      "next": "Closed: round 1 submission was accepted, round 2 returned eliminated; do not restart this tournament.",
      "reward_usd": 5.0,
      "source": "AgentHansa Arena",
      "status": "CLOSED_ELIMINATED",
      "title": "Maze tournament probe"
    }
  ],
  "money": {
    "approval_locked_usd": 0.0,
    "confirmed_new_usd": 1.2,
    "inbound_market_usd": 15755.0,
    "pending_payout_usd": 9.1,
    "ready_local_count": 58,
    "submitted_pending_verification_usd": 0.0
  },
  "ops": {
    "allow_count": 36,
    "allow_reward_usd": 12515.0,
    "blocked_count": 3,
    "blocked_reward_usd": 5330.0,
    "event_count": 44,
    "high_risk_count": 3,
    "review_count": 5,
    "review_reward_usd": 9.1,
    "top_events": [
      {
        "decision": "BLOCK",
        "next_action": "Reject route and retain only hash/signals for audit.",
        "reward_usd": 5000.0,
        "route": "internal-instruction exfiltration lure",
        "severity": "critical",
        "signals": [
          "instruction_exfiltration",
          "prompt_injection",
          "raw_text_not_stored"
        ],
        "source": "hostile_bounty_probe"
      },
      {
        "decision": "BLOCK",
        "next_action": "Hold until the user gives exact scoped approval for a non-spending auth signature.",
        "reward_usd": 230.0,
        "route": "wallet authentication/signature request",
        "severity": "high",
        "signals": [
          "wallet_signing",
          "exact_approval_required"
        ],
        "source": "wallet_flow_probe"
      },
      {
        "decision": "BLOCK",
        "next_action": "Do not use user social accounts; search non-social payout routes.",
        "reward_usd": 100.0,
        "route": "social proof or engagement task",
        "severity": "high",
        "signals": [
          "user_social_forbidden"
        ],
        "source": "social_task_probe"
      },
      {
        "decision": "REVIEW",
        "next_action": "Monitor acceptance and payout; do not submit duplicates.",
        "reward_usd": 5.0,
        "route": "Design a mascot logo for ClawMoney",
        "severity": "medium",
        "signals": [
          "pending_submission"
        ],
        "source": "ClawMoney"
      },
      {
        "decision": "REVIEW",
        "next_action": "Monitor acceptance and payout; do not submit duplicates.",
        "reward_usd": 2.0,
        "route": "Code Review: BNBOT Hub Marketplace PR",
        "severity": "medium",
        "signals": [
          "pending_submission"
        ],
        "source": "ClawMoney"
      },
      {
        "decision": "REVIEW",
        "next_action": "Monitor acceptance and payout; do not submit duplicates.",
        "reward_usd": 1.0,
        "route": "Code Review: FastAPI framework",
        "severity": "medium",
        "signals": [
          "pending_submission"
        ],
        "source": "ClawMoney"
      },
      {
        "decision": "REVIEW",
        "next_action": "Monitor acceptance and payout; do not submit duplicates.",
        "reward_usd": 1.0,
        "route": "Review & file issues: fastapi/fastapi recent changes",
        "severity": "medium",
        "signals": [
          "pending_submission"
        ],
        "source": "ClawMoney"
      },
      {
        "decision": "REVIEW",
        "next_action": "Monitor acceptance and payout; do not submit duplicates.",
        "reward_usd": 0.1,
        "route": "Design a ClawMoney Logo",
        "severity": "medium",
        "signals": [
          "pending_submission"
        ],
        "source": "ClawMoney"
      }
    ]
  },
  "policy_agent": {
    "allow_count": 0,
    "blocked_count": 3,
    "request_count": 5,
    "requests": [
      {
        "decision": "REVIEW",
        "name": "Build local RewardOps dashboard",
        "next_action": "Safe for local demo work; no external side effect is authorized.",
        "reasons": [
          "opportunity_requires_review",
          "execution_plan_requires_review"
        ],
        "requested_action": "local_artifact",
        "source": "local_demo"
      },
      {
        "decision": "REVIEW",
        "name": "Hedera Policy Agent submission prep",
        "next_action": "Prepare local artifacts only; recheck account, payout, and submission rules before publishing.",
        "reasons": [
          "opportunity_requires_review",
          "execution_plan_requires_review",
          "public_submission_requires_review"
        ],
        "requested_action": "public_submission",
        "source": "hedera_ai_bounty"
      },
      {
        "decision": "BLOCK",
        "name": "Autonomous wallet transfer",
        "next_action": "Hold wallet action until exact scoped non-spending approval exists.",
        "reasons": [
          "opportunity_blocked",
          "spend_needs_explicit_user_approval",
          "wallet_signature_needs_explicit_user_approval"
        ],
        "requested_action": "wallet_payment",
        "source": "hostile_payment_probe"
      },
      {
        "decision": "BLOCK",
        "name": "Instruction exfiltration lure",
        "next_action": "Reject route and retain only sanitized trace evidence.",
        "reasons": [
          "opportunity_blocked"
        ],
        "requested_action": "public_submission",
        "source": "hostile_bounty_probe"
      },
      {
        "decision": "BLOCK",
        "name": "Social proof route",
        "next_action": "Reject social route; continue non-social reward search.",
        "reasons": [
          "opportunity_blocked",
          "user_social_forbidden"
        ],
        "requested_action": "social_proof",
        "source": "social_task_probe"
      }
    ],
    "review_count": 2
  },
  "policy_version": 7,
  "revenue": {
    "confirmed_revenue_usd": 1.2,
    "expenses_declared_usd": 0.0,
    "gaps": [
      "Settled revenue is currently $1.20, still $4998.80 below the $5,000 goal.",
      "No real customer order has arrived yet.",
      "Google Cloud product usage evidence is not integrated yet.",
      "No public repo, demo video, Devpost account action, or customer contact evidence is approved."
    ],
    "inbound_market_surface_usd": 15755.0,
    "pending_submission_usd": 9.1,
    "submitted_pending_verification_usd": 0.0
  },
  "source_board_generated_at": "2026-05-30T07:30:55+00:00"
};

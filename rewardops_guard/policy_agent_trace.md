# RewardOps Policy Agent Trace

Generated: 2026-05-30T07:26:13+00:00
Policy version: 7
Requests: 5
Blocked: 3
Review: 2
Allowed: 0

## Decisions

- REVIEW Build local RewardOps dashboard action=local_artifact reasons=opportunity_requires_review,execution_plan_requires_review next=Safe for local demo work; no external side effect is authorized.
- REVIEW Hedera Policy Agent submission prep action=public_submission reasons=opportunity_requires_review,execution_plan_requires_review,public_submission_requires_review next=Prepare local artifacts only; recheck account, payout, and submission rules before publishing.
- BLOCK Autonomous wallet transfer action=wallet_payment reasons=opportunity_blocked,spend_needs_explicit_user_approval,wallet_signature_needs_explicit_user_approval next=Hold wallet action until exact scoped non-spending approval exists.
- BLOCK Instruction exfiltration lure action=public_submission reasons=opportunity_blocked next=Reject route and retain only sanitized trace evidence.
- BLOCK Social proof route action=social_proof reasons=opportunity_blocked,user_social_forbidden next=Reject social route; continue non-social reward search.

## Demo Fit

- Hedera Policy Agent: explicit-consent hooks before HBAR/USDC actions.
- Superteam autonomous agent: auditable task intake before blockchain/data-cloud work.
- Buyer service: compact trace proving unsafe actions were blocked before delivery.

Raw request text is intentionally not stored.

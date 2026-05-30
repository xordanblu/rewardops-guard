# RewardOps Guard Splunk Detection Pack

Generated: 2026-05-28

## Source

Import source file:

```text
rewardops_guard/ops_events.jsonl
```

Each event is sanitized. It keeps structured evidence and a hash, not raw
external bounty/task text.

## Fields

- `ts`: event timestamp.
- `event_id`: stable event identifier.
- `source`: platform or route family.
- `route`: sanitized opportunity or workflow label.
- `event_type`: normalized detection type.
- `decision`: `ALLOW`, `REVIEW`, or `BLOCK`.
- `severity`: `LOW`, `MEDIUM`, `HIGH`, or `CRITICAL`.
- `reward_usd`: advertised or relevant route value.
- `signals`: compact list of risk signals.
- `evidence_hash`: hash of supporting evidence.
- `next_action`: operator-safe next step.

## Saved Searches

### Critical Agent Prompt Exfiltration

```spl
index=rewardops sourcetype=rewardops_guard
decision=BLOCK severity=CRITICAL
signals="*instruction_exfiltration*"
| table ts source route reward_usd signals evidence_hash next_action
```

### Wallet Or Payment Action Held

```spl
index=rewardops sourcetype=rewardops_guard
decision=BLOCK signals="*wallet_signing*"
| stats count sum(reward_usd) as blocked_value by source route next_action
```

### Social Account Trap

```spl
index=rewardops sourcetype=rewardops_guard
decision=BLOCK signals="*user_social_forbidden*"
| table ts source route reward_usd evidence_hash next_action
```

### Pending Payout Queue

```spl
index=rewardops sourcetype=rewardops_guard
decision=REVIEW signals="*pending_submission*"
| stats count sum(reward_usd) as pending_value by source
```

### Allowed Inbound Surface

```spl
index=rewardops sourcetype=rewardops_guard
decision=ALLOW
| stats count sum(reward_usd) as inbound_surface by source
```

## Demo Narrative

1. Show that a malicious $5,000 prompt-injection lure is blocked before any
   repository write or public proof.
2. Show that wallet/signing and social proof routes are blocked even when a
   route advertises money.
3. Show that real inbound listings can remain visible as `ALLOW` without being
   counted as earned revenue.
4. Show that pending submissions remain in `REVIEW` until platform payout is
   spendable.

## Submission Boundary

This pack is safe for local demo use. Do not connect it to production Splunk,
publish it, or claim a hackathon route without fresh rule, account, and payout
preflight.

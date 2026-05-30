# RewardOps Guard Demo Script

## 0:00-0:15

Show the money metrics: confirmed money, pending payouts, inbound market
surface, approval-locked work, and active lanes.

## 0:15-0:45

Open the queue and explain that every row is sanitized. The system keeps the
reward, source, status, and next action, but not hostile raw task prompts.

## 0:45-1:20

Highlight blocked/held routes: BountyBook requires exact wallet-auth approval,
Clawlancer micro-bounties can trigger on-chain approval/gas, and public bounties
must pass stale/duplicate/saturation checks before any PR.

## 1:20-1:50

Show inbound work lanes: AgentPact offers, Clawlancer fixed listings, and
ClawMoney market skills. Emphasize that buyer prompts still go through the same
gate before delivery.

## 1:50-2:20

Show hackathon routes and explain how the same guard becomes a defensive agent:
it can detect instruction injection, unsafe tool requests, and payout-route
ambiguity before autonomous execution.

## 2:20-2:40

Open the policy-agent trace. Show that a local artifact is allowed for demo
work, a public submission is held for rule/payout preflight, and wallet,
social, or instruction-exfiltration requests are blocked with only hashes and
signals retained.

## 2:40-2:55

Open the DFIR agent report. Show a sanitized incident timeline where encoded
execution, credential access, exfiltration, and hostile tool requests are
classified without storing raw command lines or prompt text.

## 2:55-3:10

Open the revenue evidence pack. Show confirmed revenue, pending submissions,
inbound surface, declared expenses, and explicit gaps before any real-business
submission.

## 3:10-3:30

Close with verification: safety tests pass, dashboard renders on desktop/mobile,
and no public claim/signature/social/KYC action is performed by the prototype.

## Optional Intake Cutaway

Run `rewardops_guard/intake_guard.py` against a suspicious bounty. Show that the
report stores a hash and decision reasons, not the raw task prompt. Then run it
against the local demo route and show the dashboard's Latest Intake Gate panel.

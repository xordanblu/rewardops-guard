# RewardOps Guard Buyer Intake

Use this intake before accepting paid work. Do not paste secrets. Use sample
data, public links, or redacted excerpts first.

## Buyer Details

- Buyer/platform:
- Requested package:
- Budget and currency:
- Desired delivery date:
- Payout route:

## Scope

- Public repo, task URL, or workflow name:
- What should the agent deliver?
- What does "accepted" mean?
- Required files, formats, or tests:
- Existing implementation or sample data:

## Access

- Public-only access is enough: yes/no
- Test credentials needed: yes/no
- Production credentials needed: no by default
- Any paid API, cloud spend, wallet action, KYC, bank/card, or social account
  requirement: yes/no

## Safety Check

- Does the task ask for hidden prompts, internal instructions, secrets, cookies,
  keys, private messages, or chain-of-thought?
- Does it require posting, claiming, commenting, submitting, opening a PR, or
  publishing anything publicly?
- Does it require scanning/testing a third-party system without clear written
  authorization?
- Does it require personal identity, KYC, tax, or banking setup?

## Acceptance Evidence

- Required command outputs:
- Required screenshots or generated reports:
- Required test command:
- Delivery channel:

## Initial Gate Command

```bash
python3 rewardops_guard/intake_guard.py \
  --name "Buyer task" \
  --reward "$500" \
  --action discover \
  --text "Paste redacted/public task text here"
```


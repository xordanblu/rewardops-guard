# RewardOps Guard Public Submission Bundle

Generated: 2026-05-30T00:59:21+00:00

## Purpose

This bundle contains a sanitized local demo and evidence pack for public
hackathon review, buyer diligence, or repository publication.

## Safety Boundary

- No Devpost/forum/GitHub submission was performed by this bundle.
- No account creation, KYC, social posting, wallet signing, or spend action was performed.
- Raw external task prompts and private credentials are intentionally excluded.
- Money is counted only when spendable or visibly settled.

## Current Money Evidence

- Confirmed revenue: $1.20
- Pending ClawMoney submissions: $9.10
- Submitted pending verification after failed-audit adjustment: $0.00

## Verification

Run from the repository root:

```bash
python3 -m unittest rewardops_guard.test_revenue_evidence_pack rewardops_guard.test_hackathon_submission_builder rewardops_guard.test_ops_event_report rewardops_guard.test_policy_agent rewardops_guard.test_find_evil_defender_demo rewardops_guard.test_dfir_agent_demo safety_gate.test_protective_pipeline safety_gate.test_safety_gate
python3 rewardops_guard/build_dashboard.py

cd find_evil_rewardops_defender
python3 -m unittest discover -s tests
./run_terminal_demo.sh
```

## FIND EVIL Defender Package

`find_evil_rewardops_defender/` contains the standalone RewardOps Defender
package prepared for the FIND EVIL prize route. It includes a terminal demo,
DFIR triage module, agent-defense sequence detector, publication guard,
accuracy report, architecture diagram, sample events, tests, and submission
draft.

The latest local verification produced:

- 14 unit tests passing.
- DFIR report: 5 events, 5 findings, critical severity.
- Agent-defense verdict:
  `agent_tool_abuse+credential_theft_with_exfiltration+scripted_execution_chain`.
- Publication guard: `release_ready`, 0 blocking secret findings, 19
  prompt-injection fixtures counted as evidence rather than instructions.

## Current Manifest

The current complete file manifest is `manifest.json`. The hash list below is
kept as the original bundle inventory reference; `manifest.json` supersedes it
for files changed by later publication hardening.

## Initial Bundle Files

- `rewardops_guard/README.md` sha256=1dbee345b349b71077eaa3fb81c4cf5c66c0ad5f872357c9e5811bb87235a496
- `rewardops_guard/index.html` sha256=491cbea4d24666a643110ea57350901c0c17c6e47e41a3759e2574f81c55a7b3
- `rewardops_guard/data.js` sha256=338dfa502b579fc9f756bb3292b896c27d565fd2acd9cb4a153cc3af0eaca75d
- `rewardops_guard/demo_script.md` sha256=a4cd491502027e3e87207d58cd1f6bd55e45a60c311c53cb3ce2978ae8cc15bf
- `rewardops_guard/submission_packet.md` sha256=90591f4a9fe62b8a56fcbf73719a5db6d69b918511753f9ea69005b56fad8b88
- `rewardops_guard/hackathon_submission_pack.md` sha256=d999faaa55836768c43c5060be950e7495a950bd1b715ff358f8e14044f1f3db
- `rewardops_guard/hackathon_submission_pack.json` sha256=5f050020eb30be1fba912ffb6364b099e7efa9d99628c2f8837558ee8f66fee4
- `rewardops_guard/revenue_evidence_pack.md` sha256=1eb94a4ee58a51c0541569c967a9c52ee96ee8ab3d5604d66998f1d31a9a41c0
- `rewardops_guard/revenue_evidence_pack.json` sha256=769b4c969a513a180a87c58cab8487eebbb4ea61fedf3c469ae2a6e9f5ea9c15
- `rewardops_guard/ops_event_report.md` sha256=dcde613474699f66f9a65a31aca1f26e8910d76b0eef82db796d7840982d3810
- `rewardops_guard/ops_event_report.json` sha256=a03988c0a4ddc050a4f06a75e09650a66f330ce9933445d105ae458b4180928c
- `rewardops_guard/ops_events.jsonl` sha256=2de29fdb68d59739f16b8456e56c16c6d929df8cb5ddfe6fe2041058f61d762a
- `rewardops_guard/policy_agent_trace.md` sha256=8389305ec6e545d172cd75998098140a140be16073e0b6c70d420e5ea76bcee5
- `rewardops_guard/policy_agent_trace.json` sha256=bb9a1bee26b42ed8bdceba062763850b7d6027140339dd58f1aa661c3a835956
- `rewardops_guard/find_evil_defender_report.md` sha256=f82695d233c2b27c1d69edfe58c8f8350eeaf6662644e33d2170029846db1658
- `rewardops_guard/find_evil_defender_report.json` sha256=423a85d6637e612c1f37ab1c225dee3db3534487fc57a051523fc7d6272ddd80
- `rewardops_guard/dfir_agent_report.md` sha256=cb5c6a12b38c9c558591280b122a9ae4b142c3d0dd1ab7c8ecfd84a555ef6bb0
- `rewardops_guard/dfir_agent_report.json` sha256=d83ecbc63a14b50ae197fb4cf03e95cd405f22ae10c0b96259068c2fb56ed6ea
- `rewardops_guard/splunk_detection_pack.md` sha256=15a3a97b0dee6dc5f34c847d05e816ac5c45b4bb610e6f5c5c1a7c3531afa6b8
- `rewardops_guard/service_menu.md` sha256=90e34b4db5984afeded7993265e0fcd0ff438d322e652c93b5a72a1a46b312f5
- `rewardops_guard/buyer_onepager.md` sha256=20cfdcde8aa156c1aa29f83d0600e4337721f79850e8d103debbe390b2164c29
- `rewardops_guard/buyer_intake.md` sha256=ee133394d94603ce6e7011a90f164f87871116f5da1ab36855f18bdf9c08801d
- `rewardops_guard/proposal_templates.md` sha256=61c9539f7ea61f1e36a416cf0488b4ecf63a023b39b42c43bc513702ba89a3d8
- `rewardops_guard/clawmoney_skill_fulfillment_pack.md` sha256=f5eadf683ae84878225838a8023ceecd09e2063e857e28403232411c5689f776
- `rewardops_guard/clawmoney_skill_fulfillment_pack.json` sha256=c07df4398811de514d3e6c6996e4ecfe3ce717a8c796b491bb3393e9b4f6612a
- `rewardops_guard/goal5000_current_routes.md` sha256=b012baefcf58b700fb760b42ca39d789bf1ed879a3c9288fdf44ba77d1ebd5af
- `rewardops_guard/revenue_evidence_pack.py` sha256=374169b42d8134133be2b34e1500a395003a53d2d65979f6818fef2635c6de84
- `rewardops_guard/hackathon_submission_builder.py` sha256=c7e32db54663258dd2056124b1841a293d38fc77dbfa26d222bd3b14f09c2865
- `rewardops_guard/build_dashboard.py` sha256=93ae303ba94aa2d0034b2b5fd4c2be7849c10f1cdf9d2283c5aba5cffba5dff0
- `rewardops_guard/ops_event_report.py` sha256=962a18bdf58219cb248a97e3fe2758021893f23d28cf440f849e2164466528c2
- `rewardops_guard/policy_agent.py` sha256=0ef986b5f4e9c3a90a79a0f11c8bc1be613f69e61177070dfd995623ce21ff70
- `rewardops_guard/find_evil_defender_demo.py` sha256=8d8b4dfb44b1c03e69d4efb6ae92dd561237f7dde4dece3fc430c06d3502bc13
- `rewardops_guard/dfir_agent_demo.py` sha256=6aefc1d8d2d4c409edc321d95c4b9d8e136cc56adc972c19c2be9389f017d705
- `rewardops_guard/simulate_ops_events.py` sha256=f32a930fe28a4cad27874f769414705e69ff3eef77605fda5733ac1024f2f77e
- `safety_gate/README.md` sha256=f536f77d455449914b7fa204eac58702c8d52dc7fae6e1b4ec184df107008e93
- `safety_gate/policy.json` sha256=84f37bed8e0e044f2065d322fb541b0986b76765a247d617cb7fd4e04c31a4b1
- `safety_gate/protective_pipeline.py` sha256=af978933a6bc834c6462f302ca07f6ad0039a2c8d9f12976eeed60a400ce6ddc
- `safety_gate/safety_gate.py` sha256=d4d13e68b5af30e023d53be1fa116f725bda2b28558686092df3f0bfd1cc28fc
- `rewardops_guard/test_revenue_evidence_pack.py` sha256=7498694fb15415197cc41801b7c0100d9b4a36a5ad8ece538edd514733bc181c
- `rewardops_guard/test_hackathon_submission_builder.py` sha256=5215edf73648522250350b159644cba6c877cee6d63a41dfe669943c7a927d1d
- `rewardops_guard/test_ops_event_report.py` sha256=0854fa6bee60421a89ace48273b7089c5c6b642b2274b37563d49a3bd444fbbf
- `rewardops_guard/test_policy_agent.py` sha256=48ed08bb67d811098d899ee878e6fe60ebc3e610be62ee83fa382a4625272e22
- `rewardops_guard/test_find_evil_defender_demo.py` sha256=18571abbaf3602a8a089522b6389bb1b6d2148c34f77c5d59312506207eaf50f
- `rewardops_guard/test_dfir_agent_demo.py` sha256=34892e4a86c007b56176fa50f9bbb1b3987c43b28243cd3a7aaad58ee1bb53f6
- `safety_gate/test_protective_pipeline.py` sha256=c2275dcffedd1fa0672a62f04338727a843661bc62d65d74ca8bcc4b027f60d2
- `safety_gate/test_safety_gate.py` sha256=62f1f0de8d25725c278b1a70f4341ddc54e0781236e71f01a4970d52f73608db

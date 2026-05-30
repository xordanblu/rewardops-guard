# RewardOps Defender Report

Generated: 2026-05-30T13:08:22Z
Case: find-evil-agent-defense
Verdict: agent_tool_abuse+credential_theft_with_exfiltration+scripted_execution_chain
Events: 6
High/Critical events: 4
Self-corrections: 2

## Hypotheses

- HIGH agent_tool_abuse: external content attempted to control the agent or trigger payment-capable approval
- HIGH credential_theft_with_exfiltration: credential material access and outbound transfer appeared in the same host timeline
- MEDIUM scripted_execution_chain: encoded shell activity preceded higher-risk endpoint or network signals

## Timeline

- 2026-05-29T18:00:02Z LOW agent-runner training_doc/web_content signals=agent_prompt_injection,obfuscated_prompt_smuggling hash=ab6542445d68
- 2026-05-29T18:01:14Z CRITICAL agent-runner mcp/tool_request signals=agent_prompt_injection,obfuscated_prompt_smuggling hash=f307bb8a43f5
- 2026-05-29T18:01:45Z HIGH agent-runner wallet/approval_request signals=wallet_trap hash=7724244aa293
- 2026-05-29T18:02:20Z MEDIUM workstation-17 endpoint/process signals=encoded_execution hash=883e2f0476b2
- 2026-05-29T18:02:51Z HIGH workstation-17 endpoint/credential_access signals=credential_access hash=e0bac49639d7
- 2026-05-29T18:03:04Z CRITICAL workstation-17 network/egress signals=credential_access,exfiltration hash=ef0faca8b969

## Response Plan

- triage: rank events by sequence, source, score, and whether a tool side effect was requested (local-safe)
- scope: scope affected hosts: agent-runner, workstation-17 (local-safe)
- agent_control: block prompt-exfiltration and wallet-signing lures before shell, browser, git, or wallet tools run (local-safe)
- contain: pause unsafe agent tools and isolate affected endpoint hosts after operator approval (approval-required)
- recover: restore normal tool access only after policy hooks block replayed probes (local-safe)

Raw event details are intentionally hashed and not stored.

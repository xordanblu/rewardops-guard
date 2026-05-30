# RewardOps DFIR Agent Report

Generated: 2026-05-29T18:17:19+00:00
Verdict: probable_credential_theft_with_exfiltration+agent_prompt_injection
Events: 5
High/Critical events: 2
Affected hosts: agent-runner, workstation-17

## Timeline

- 2026-05-28T20:00:02Z MEDIUM workstation-17 endpoint/process signals=encoded_execution hash=12fa2b9ac444
- 2026-05-28T20:00:29Z MEDIUM workstation-17 endpoint/process signals=credential_access hash=e0bac49639d7
- 2026-05-28T20:01:04Z CRITICAL workstation-17 network/egress signals=credential_access,exfiltration hash=ef0faca8b969
- 2026-05-28T20:01:22Z CRITICAL agent-runner mcp/tool_call signals=exfiltration,unsafe_tool_request hash=a379e4e56594
- 2026-05-28T20:02:10Z INFO agent-runner policy/decision signals=none hash=b75eb60e9845

## Recommended Actions

- Isolate affected hosts: agent-runner, workstation-17.
- Rotate credentials only after preserving evidence and confirming scope.
- Preserve source artifacts and collect hashes before enrichment.
- Keep all irreversible containment actions behind human approval.
- Do not expose credentials, prompts, or raw logs in the report.
- Disable unsafe tool surface and require policy review before more tool calls.

Raw event details are intentionally hashed and not stored.

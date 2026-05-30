# Screencast Script

Target length: under 10 minutes.

Format: live terminal execution with narration. No slides, no marketing-only footage.

## Opening

This is RewardOps Defender, a local read-only defensive triage agent for
sanitized incident and agent-tool evidence. It does not probe live systems,
execute malware, use credentials, sign wallets, or perform remediation. The
demo shows a reproducible agent loop: tests, case triage, JSON-RPC tool call,
agent-defense sequence analysis, accuracy validation, and audit trail.

## Terminal Steps

```bash
./run_terminal_demo.sh
```

Narration points while it runs:

1. The tests prove redaction, rule scoring, self-correction, report export, and the read-only tool wrapper.
2. The sample evidence contains five events: encoded PowerShell, public egress, failed login, suspicious DLL write, and a private-network egress probe.
3. The self-correction pass removes the private-network event from the final public-egress findings.
4. The agent-defense sequence adds prompt-injection, wallet-signing, endpoint credential access, and exfiltration signals.
5. The defender downgrades a benign training-document phrase while keeping live tool and wallet requests high risk.
6. The accuracy report compares labelled expected rules to observed rules and reports precision/recall.
7. The audit trail records every event hash, matched rules, and correction count so findings are traceable without exposing raw secrets.

## Close

The current prototype is intentionally bounded. A stronger version would plug
the same interface into SIFT/Protocol SIFT tools for real evidence types while
keeping the same safety guarantees: local read-only inputs, redaction before
reporting, explicit audit trail, and human approval before containment or
credential rotation.

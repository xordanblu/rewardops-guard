#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUT="$ROOT/out"
EVENTS="$ROOT/dfir_triage_agent/sample_events.jsonl"
AGENT_EVENTS="$ROOT/dfir_triage_agent/sample_agent_events.jsonl"

cd "$ROOT"
mkdir -p "$OUT"

echo "== RewardOps DFIR Agent terminal demo =="
echo "Local read-only run. No network calls, account actions, wallet actions, live probing, or destructive remediation."
echo

echo "== 1. Run deterministic tests =="
python3 -m unittest discover -s tests
echo

echo "== 2. Export DFIR triage report =="
python3 dfir_triage_agent/dfir_triage.py \
  --events "$EVENTS" \
  --json-output "$OUT/dfir_triage_report.json" \
  --markdown-output "$OUT/dfir_triage_report.md" \
  --case-id find-evil-demo
echo

echo "== 3. Exercise read-only JSON-RPC tool wrapper =="
python3 -m dfir_triage_agent.mcp_server --oneshot \
  '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"triage_case","arguments":{"path":"dfir_triage_agent/sample_events.jsonl","case_id":"find-evil-mcp"}}}'
echo

echo "== 4. Export agent-defense sequence report =="
python3 dfir_triage_agent/rewardops_defender.py \
  --events "$AGENT_EVENTS" \
  --json-output "$OUT/rewardops_defender_report.json" \
  --markdown-output "$OUT/rewardops_defender_report.md" \
  --case-id find-evil-agent-defense
echo

echo "== 5. Build local publication-safety manifest =="
python3 dfir_triage_agent/submission_guard.py \
  --root "$ROOT" \
  --json-output "$OUT/submission_guard_manifest.json"
echo

echo "== 6. Run labelled FIND EVIL local case =="
python3 dfir_triage_agent/case_runner.py \
  --case-json "$ROOT/cases/find_evil_local_case.json" \
  --json-output "$OUT/find_evil_case_report.json" \
  --markdown-output "$OUT/find_evil_case_report.md"
echo

echo "== 7. Show reviewer-facing Markdown report =="
sed -n '1,120p' "$OUT/dfir_triage_report.md"
echo
sed -n '1,120p' "$OUT/rewardops_defender_report.md"
echo
sed -n '1,120p' "$OUT/find_evil_case_report.md"

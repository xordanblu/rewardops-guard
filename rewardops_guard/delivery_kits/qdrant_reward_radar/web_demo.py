#!/usr/bin/env python3
"""Local web demo for Qdrant Reward Route Radar."""

from __future__ import annotations

import argparse
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
from urllib.parse import parse_qs, urlparse
from typing import Any

if __package__ in {None, ""}:
    import sys

    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from rewardops_guard.delivery_kits.qdrant_reward_radar import reward_radar


DEFAULT_QUERY = "non-chatbot vector search hackathon with safety ranking"


def coerce_float(value: Any, default: float) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def coerce_int(value: Any, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def coerce_bool(value: Any, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return default
    return str(value).lower() in {"1", "true", "yes", "on"}


def build_search_payload(params: dict[str, Any]) -> dict[str, Any]:
    query = str(params.get("query") or DEFAULT_QUERY).strip() or DEFAULT_QUERY
    min_reward = coerce_float(params.get("min_reward"), 1000.0)
    max_risk = coerce_int(params.get("max_risk"), 5)
    allow_review = coerce_bool(params.get("allow_review"), True)
    report = reward_radar.build_demo_report(
        query=query,
        min_reward=min_reward,
        max_risk=max_risk,
        allow_review=allow_review,
    )
    blocked = [
        item
        for item in reward_radar.load_opportunities()
        if reward_radar.safety_decision(item)["decision"] == "BLOCK"
    ]
    return {
        **report,
        "controls": {
            "query": query,
            "min_reward": min_reward,
            "max_risk": max_risk,
            "allow_review": allow_review,
        },
        "blocked_fixture_count": len(blocked),
        "blocked_fixture_ids": [item["id"] for item in blocked],
    }


def render_page() -> str:
    return """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Qdrant Reward Route Radar</title>
  <style>
    :root {
      color-scheme: light;
      --ink: #17202a;
      --muted: #5c6675;
      --line: #d7dde6;
      --panel: #ffffff;
      --page: #f5f7fb;
      --teal: #0f766e;
      --blue: #2563eb;
      --amber: #b45309;
      --red: #b91c1c;
      --green: #15803d;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      background: var(--page);
      color: var(--ink);
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      line-height: 1.45;
    }
    header {
      border-bottom: 1px solid var(--line);
      background: #ffffff;
    }
    .wrap {
      width: min(1180px, calc(100vw - 32px));
      margin: 0 auto;
    }
    .topbar {
      min-height: 92px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 24px;
    }
    h1 {
      margin: 0;
      font-size: 26px;
      font-weight: 760;
      letter-spacing: 0;
    }
    .subtitle {
      margin-top: 6px;
      color: var(--muted);
      font-size: 14px;
    }
    .badges {
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
      justify-content: flex-end;
    }
    .badge {
      border: 1px solid var(--line);
      border-radius: 999px;
      background: #f9fafb;
      padding: 6px 10px;
      color: #334155;
      font-size: 12px;
      font-weight: 650;
      white-space: nowrap;
    }
    main {
      padding: 22px 0 36px;
    }
    .layout {
      display: grid;
      grid-template-columns: 360px minmax(0, 1fr);
      gap: 18px;
      align-items: start;
    }
    section {
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
    }
    .controls {
      padding: 18px;
    }
    .controls h2,
    .results h2,
    .policy h2 {
      margin: 0 0 14px;
      font-size: 15px;
      font-weight: 760;
      letter-spacing: 0;
    }
    label {
      display: block;
      margin: 14px 0 6px;
      color: #334155;
      font-size: 12px;
      font-weight: 700;
    }
    textarea,
    input[type="number"],
    input[type="range"] {
      width: 100%;
    }
    textarea,
    input[type="number"] {
      border: 1px solid #cbd5e1;
      border-radius: 6px;
      padding: 10px 11px;
      color: var(--ink);
      background: #ffffff;
      font: inherit;
      font-size: 14px;
    }
    textarea {
      min-height: 116px;
      resize: vertical;
    }
    .checkrow {
      display: flex;
      align-items: center;
      gap: 8px;
      margin: 14px 0 18px;
      color: #334155;
      font-size: 14px;
    }
    button {
      width: 100%;
      border: 0;
      border-radius: 6px;
      background: var(--teal);
      color: white;
      padding: 11px 12px;
      font: inherit;
      font-weight: 760;
      cursor: pointer;
    }
    button:focus-visible,
    textarea:focus-visible,
    input:focus-visible {
      outline: 3px solid rgba(37, 99, 235, 0.24);
      outline-offset: 2px;
    }
    .policy {
      margin-top: 14px;
      padding: 16px 18px;
    }
    .policy ul {
      margin: 0;
      padding-left: 18px;
      color: var(--muted);
      font-size: 13px;
    }
    .results {
      overflow: hidden;
    }
    .results-head {
      padding: 17px 18px;
      border-bottom: 1px solid var(--line);
      display: flex;
      justify-content: space-between;
      gap: 16px;
      align-items: center;
    }
    .summary {
      color: var(--muted);
      font-size: 13px;
      text-align: right;
    }
    table {
      width: 100%;
      border-collapse: collapse;
      font-size: 13px;
    }
    th,
    td {
      border-bottom: 1px solid #e5e9f0;
      padding: 11px 12px;
      text-align: left;
      vertical-align: top;
    }
    th {
      background: #f8fafc;
      color: #475569;
      font-size: 12px;
      font-weight: 760;
    }
    .money {
      color: var(--green);
      font-weight: 760;
      white-space: nowrap;
    }
    .risk {
      color: var(--amber);
      font-weight: 760;
      white-space: nowrap;
    }
    .route-title {
      font-weight: 760;
      margin-bottom: 3px;
    }
    .route-link {
      color: var(--blue);
      overflow-wrap: anywhere;
      text-decoration: none;
    }
    .route-link:hover {
      text-decoration: underline;
    }
    .action {
      color: #334155;
      max-width: 360px;
    }
    .empty {
      padding: 34px 18px;
      color: var(--muted);
    }
    .blocked {
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
      padding: 14px 18px 18px;
      color: var(--muted);
      font-size: 12px;
    }
    .blocked span {
      border: 1px solid #fecaca;
      border-radius: 999px;
      background: #fff7f7;
      color: var(--red);
      padding: 5px 9px;
      font-weight: 700;
    }
    @media (max-width: 860px) {
      .topbar,
      .results-head {
        align-items: flex-start;
        flex-direction: column;
      }
      .badges,
      .summary {
        justify-content: flex-start;
        text-align: left;
      }
      .layout {
        grid-template-columns: 1fr;
      }
      table {
        min-width: 760px;
      }
      .results {
        overflow-x: auto;
      }
    }
  </style>
</head>
<body>
  <header>
    <div class="wrap topbar">
      <div>
        <h1>Qdrant Reward Route Radar</h1>
        <div class="subtitle">Vector search triage for high-upside reward routes with safety filters.</div>
      </div>
      <div class="badges" aria-label="demo properties">
        <span class="badge">Qdrant vector index</span>
        <span class="badge">Payload safety filters</span>
        <span class="badge">No social accounts</span>
      </div>
    </div>
  </header>
  <main>
    <div class="wrap layout">
      <div>
        <section class="controls" aria-labelledby="controls-title">
          <h2 id="controls-title">Search Controls</h2>
          <label for="query">Opportunity intent</label>
          <textarea id="query">non-chatbot vector search hackathon with safety ranking</textarea>
          <label for="min_reward">Minimum reward USD</label>
          <input id="min_reward" type="number" min="0" step="100" value="1000">
          <label for="max_risk">Maximum risk: <span id="risk_value">5</span></label>
          <input id="max_risk" type="range" min="1" max="9" value="5">
          <label class="checkrow" for="allow_review">
            <input id="allow_review" type="checkbox" checked>
            Include routes that need human review
          </label>
          <button id="run" type="button">Run Search</button>
        </section>
        <section class="policy" aria-labelledby="policy-title">
          <h2 id="policy-title">Hard Filters</h2>
          <ul>
            <li>Blocks social-account requirements.</li>
            <li>Blocks wallet-signing and spending routes.</li>
            <li>Blocks secret or internal-instruction disclosure.</li>
            <li>Holds KYC/payment-document routes for review.</li>
            <li>Counts money only after payout or visible settlement.</li>
          </ul>
        </section>
      </div>
      <section class="results" aria-labelledby="results-title">
        <div class="results-head">
          <h2 id="results-title">Ranked Routes</h2>
          <div class="summary" id="summary">Loading...</div>
        </div>
        <div id="table-host" class="empty">Loading routes...</div>
        <div id="blocked" class="blocked" aria-live="polite"></div>
      </section>
    </div>
  </main>
  <script>
    const fields = {
      query: document.getElementById("query"),
      minReward: document.getElementById("min_reward"),
      maxRisk: document.getElementById("max_risk"),
      allowReview: document.getElementById("allow_review"),
      run: document.getElementById("run"),
      riskValue: document.getElementById("risk_value"),
      summary: document.getElementById("summary"),
      tableHost: document.getElementById("table-host"),
      blocked: document.getElementById("blocked"),
    };

    function money(value) {
      return "$" + Number(value).toLocaleString("en-US", { maximumFractionDigits: 0 });
    }

    function escapeHtml(value) {
      return String(value)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;");
    }

    async function runSearch() {
      fields.riskValue.textContent = fields.maxRisk.value;
      fields.summary.textContent = "Running Qdrant search...";
      const params = new URLSearchParams({
        query: fields.query.value,
        min_reward: fields.minReward.value,
        max_risk: fields.maxRisk.value,
        allow_review: fields.allowReview.checked ? "true" : "false",
      });
      const response = await fetch("/api/search?" + params.toString());
      const data = await response.json();
      const routes = data.ranked_routes || [];
      fields.summary.textContent =
        data.indexed_opportunities + " indexed, " + routes.length + " route shown, " +
        data.blocked_fixture_count + " unsafe fixtures blocked";
      fields.blocked.innerHTML = (data.blocked_fixture_ids || [])
        .map((id) => "<span>" + escapeHtml(id) + "</span>")
        .join("");
      if (!routes.length) {
        fields.tableHost.className = "empty";
        fields.tableHost.textContent = "No routes matched the current reward and risk filters.";
        return;
      }
      fields.tableHost.className = "";
      fields.tableHost.innerHTML = `
        <table>
          <thead>
            <tr>
              <th>Rank</th>
              <th>Route</th>
              <th>Reward</th>
              <th>Risk</th>
              <th>Score</th>
              <th>Next action</th>
            </tr>
          </thead>
          <tbody>
            ${routes.map((route, index) => `
              <tr>
                <td>${index + 1}</td>
                <td>
                  <div class="route-title">${escapeHtml(route.title)}</div>
                  <a class="route-link" href="${escapeHtml(route.url)}">${escapeHtml(route.route_id)}</a>
                </td>
                <td class="money">${money(route.reward_usd)}</td>
                <td class="risk">${escapeHtml(route.risk_level)}</td>
                <td>${escapeHtml(route.score)}</td>
                <td class="action">${escapeHtml(route.action)}</td>
              </tr>
            `).join("")}
          </tbody>
        </table>`;
    }

    fields.maxRisk.addEventListener("input", () => {
      fields.riskValue.textContent = fields.maxRisk.value;
    });
    fields.run.addEventListener("click", runSearch);
    runSearch().catch((error) => {
      fields.summary.textContent = "Search failed";
      fields.tableHost.className = "empty";
      fields.tableHost.textContent = String(error);
    });
  </script>
</body>
</html>
"""


class Handler(BaseHTTPRequestHandler):
    server_version = "RewardRadarDemo/1.0"

    def log_message(self, format: str, *args: Any) -> None:
        return

    def send_json(self, payload: dict[str, Any], status: HTTPStatus = HTTPStatus.OK) -> None:
        body = json.dumps(payload, indent=2, sort_keys=True).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path in {"/", "/index.html"}:
            body = render_page().encode("utf-8")
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        if parsed.path == "/api/search":
            query = parse_qs(parsed.query)
            params = {key: values[-1] for key, values in query.items()}
            try:
                self.send_json(build_search_payload(params))
            except Exception as exc:
                self.send_json({"error": str(exc)}, HTTPStatus.INTERNAL_SERVER_ERROR)
            return
        self.send_error(HTTPStatus.NOT_FOUND)


def serve(host: str, port: int) -> None:
    with ThreadingHTTPServer((host, port), Handler) as server:
        print(f"Serving Qdrant Reward Route Radar at http://{host}:{port}", flush=True)
        server.serve_forever()


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the Qdrant Reward Route Radar local web demo.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8787)
    args = parser.parse_args()
    serve(args.host, args.port)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Dependency-free local web demo for FHIR Care Brief Agent."""

from __future__ import annotations

import argparse
import html
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import sys
from typing import Any
from urllib.parse import parse_qs, urlparse

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from rewardops_guard.delivery_kits.intersystems_fhir_agent_pack.fhir_summary_agent import (
    ROLE_GUIDANCE,
    FhirSummary,
    load_bundle,
    summarize_bundle,
)


KIT_ROOT = Path(__file__).resolve().parent


def list_items(items: list[str]) -> str:
    return "\n".join(f"<li>{html.escape(item)}</li>" for item in items)


def render_demo_html(summary: FhirSummary, role_key: str) -> str:
    role_links = " ".join(
        f'<a class="role {("active" if key == role_key else "")}" href="/?role={html.escape(key)}">{html.escape(value["label"])}</a>'
        for key, value in ROLE_GUIDANCE.items()
    )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>FHIR Care Brief Agent</title>
  <style>
    :root {{
      color-scheme: light;
      --ink: #18212f;
      --muted: #5b6675;
      --line: #d8dee8;
      --surface: #f7f9fc;
      --panel: #ffffff;
      --accent: #0f766e;
      --accent-soft: #d7f4ef;
      --warn: #a16207;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      color: var(--ink);
      background: var(--surface);
    }}
    header {{
      padding: 28px min(5vw, 48px) 18px;
      border-bottom: 1px solid var(--line);
      background: var(--panel);
    }}
    h1 {{
      margin: 0 0 8px;
      font-size: clamp(26px, 4vw, 44px);
      line-height: 1.05;
      font-weight: 760;
      letter-spacing: 0;
    }}
    .subtitle {{
      margin: 0;
      max-width: 960px;
      color: var(--muted);
      font-size: 16px;
      line-height: 1.5;
    }}
    nav {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-top: 18px;
    }}
    .role {{
      display: inline-flex;
      min-height: 36px;
      align-items: center;
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 0 12px;
      color: var(--ink);
      background: var(--panel);
      text-decoration: none;
      font-size: 14px;
      font-weight: 650;
    }}
    .role.active {{
      border-color: var(--accent);
      background: var(--accent-soft);
      color: #064e48;
    }}
    main {{
      width: min(1200px, 100%);
      margin: 0 auto;
      padding: 24px min(5vw, 48px) 36px;
    }}
    .summary-bar {{
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 12px;
      margin-bottom: 18px;
    }}
    .metric, section {{
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--panel);
    }}
    .metric {{
      padding: 14px 16px;
    }}
    .metric span {{
      display: block;
      color: var(--muted);
      font-size: 12px;
      text-transform: uppercase;
      letter-spacing: .08em;
    }}
    .metric strong {{
      display: block;
      margin-top: 4px;
      font-size: 20px;
      line-height: 1.2;
    }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 14px;
    }}
    section {{
      min-height: 220px;
      padding: 18px;
    }}
    section.trace {{
      grid-column: 1 / -1;
      min-height: 120px;
    }}
    h2 {{
      margin: 0 0 12px;
      font-size: 17px;
      line-height: 1.3;
      letter-spacing: 0;
    }}
    ul {{
      margin: 0;
      padding-left: 20px;
    }}
    li {{
      margin: 8px 0;
      line-height: 1.45;
    }}
    code {{
      color: var(--warn);
      font-size: 13px;
      overflow-wrap: anywhere;
    }}
    @media (max-width: 760px) {{
      .summary-bar, .grid {{
        grid-template-columns: 1fr;
      }}
      section.trace {{
        grid-column: auto;
      }}
    }}
  </style>
</head>
<body>
  <header>
    <h1>FHIR Care Brief Agent</h1>
    <p class="subtitle">Synthetic-data-first patient summaries with medication safety, care-plan tasks, and evidence traceability. Current role: <strong>{html.escape(summary.role)}</strong>.</p>
    <nav aria-label="Summary roles">{role_links}</nav>
  </header>
  <main>
    <div class="summary-bar">
      <div class="metric"><span>Patient</span><strong>{html.escape(summary.patient_label)}</strong></div>
      <div class="metric"><span>Role</span><strong>{html.escape(summary.role)}</strong></div>
      <div class="metric"><span>API</span><strong><code>/summary.json?role={html.escape(role_key)}</code></strong></div>
    </div>
    <div class="grid">
      <section><h2>Current Issues</h2><ul>{list_items(summary.current_issues)}</ul></section>
      <section><h2>Recent Changes</h2><ul>{list_items(summary.recent_changes)}</ul></section>
      <section><h2>Risks / Follow-Up</h2><ul>{list_items(summary.risks_follow_up)}</ul></section>
      <section><h2>Medication Safety</h2><ul>{list_items(summary.medication_safety)}</ul></section>
      <section><h2>Care Plan Next Steps</h2><ul>{list_items(summary.care_plan_next_steps)}</ul></section>
      <section class="trace"><h2>Evidence Trace</h2><ul>{list_items(summary.evidence_trace)}</ul></section>
    </div>
  </main>
</body>
</html>
"""


def selected_role(path: str) -> str:
    query = parse_qs(urlparse(path).query)
    requested = query.get("role", ["ed_doctor"])[0]
    return requested if requested in ROLE_GUIDANCE else "ed_doctor"


class DemoHandler(BaseHTTPRequestHandler):
    bundle_path = KIT_ROOT / "sample_patient_bundle.json"

    def do_GET(self) -> None:
        role = selected_role(self.path)
        summary = summarize_bundle(load_bundle(self.bundle_path), role)
        parsed_path = urlparse(self.path).path
        if parsed_path == "/summary.json":
            self.send_json(summary.as_dict())
            return
        if parsed_path in {"/", "/index.html"}:
            self.send_html(render_demo_html(summary, role))
            return
        self.send_response(404)
        self.end_headers()

    def log_message(self, format: str, *args: object) -> None:
        return

    def send_html(self, body: str) -> None:
        payload = body.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def send_json(self, data: dict[str, Any]) -> None:
        payload = json.dumps(data, indent=2, sort_keys=True).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)


def run_server(host: str, port: int) -> None:
    server = ThreadingHTTPServer((host, port), DemoHandler)
    print(f"FHIR Care Brief Agent demo: http://{host}:{server.server_port}")
    try:
        server.serve_forever()
    finally:
        server.server_close()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    run_server(args.host, args.port)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

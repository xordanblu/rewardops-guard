#!/usr/bin/env python3
"""Preflight report for the Qdrant Reward Route Radar hackathon package."""

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import sys
from typing import Any

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from rewardops_guard.delivery_kits.qdrant_reward_radar import reward_radar


KIT_ROOT = Path(__file__).resolve().parent
REQUIRED_FILES = [
    "README.md",
    "SUBMISSION_DRAFT.md",
    "requirements.txt",
    "sample_opportunities.json",
    "reward_radar.py",
    "web_demo.py",
    "test_reward_radar.py",
    "VIDEO_SCRIPT.md",
    "demo_video/DESIGN.md",
    "demo_video/index.html",
    "demo_video/VIDEO_MANIFEST.md",
    "demo_video/renders/qdrant_reward_route_radar_demo.mp4",
    "demo_video/renders/qdrant_reward_route_radar_contact_sheet.png",
    "demo_video/renders/qdrant_reward_route_radar_hero_frames.png",
]
EXTERNAL_GATES = [
    "Register for Qdrant Think Outside the Bot Hackathon",
    "Publish or share a GitHub repository with organizers",
    "Record and host a demo video of no more than 3 minutes",
    "Submit through the Qdrant hackathon form before 2026-06-01 23:59 PT",
    "Provide prize identity/payment documentation only if selected",
]


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def qdrant_available() -> bool:
    return reward_radar.QdrantClient is not None


def demo_smoke() -> dict[str, Any]:
    if not qdrant_available():
        return {"ok": False, "reason": "qdrant-client not installed"}
    report = reward_radar.build_demo_report(
        "non-chatbot vector search hackathon reward route safety radar",
        min_reward=1000,
        allow_review=True,
    )
    route_ids = [route["route_id"] for route in report["ranked_routes"]]
    return {
        "ok": "qdrant-vsd-2026" in route_ids and "unsafe-instruction-leak-bounty" not in route_ids,
        "route_ids": route_ids,
        "indexed_opportunities": report["indexed_opportunities"],
    }


def build_report() -> dict[str, Any]:
    missing = [path for path in REQUIRED_FILES if not (KIT_ROOT / path).exists()]
    smoke = demo_smoke()
    web_demo_ok = False
    try:
        from rewardops_guard.delivery_kits.qdrant_reward_radar import web_demo

        page = web_demo.render_page()
        web_demo_ok = "Qdrant Reward Route Radar" in page and "/api/search" in page
    except Exception:
        web_demo_ok = False
    video_path = KIT_ROOT / "demo_video" / "renders" / "qdrant_reward_route_radar_demo.mp4"
    video_ok = video_path.exists() and video_path.stat().st_size > 1_000_000
    return {
        "generated_at": now_iso(),
        "project": "Qdrant Reward Route Radar",
        "hackathon": {
            "name": "Qdrant Think Outside the Bot Virtual Hackathon",
            "source": "https://try.qdrant.tech/hackathon-vsd",
            "first_prize_usd": 5000,
            "deadline": "2026-06-01 23:59 PT",
            "non_chatbot_positioning": "A vector-search ranking surface for reward operations, not a conversational Q&A bot.",
        },
        "required_files": [{"path": path, "exists": (KIT_ROOT / path).exists()} for path in REQUIRED_FILES],
        "missing_required_files": missing,
        "qdrant_client_available": qdrant_available(),
        "demo_smoke": smoke,
        "web_demo_ok": web_demo_ok,
        "video_ok": video_ok,
        "local_ok": not missing and smoke["ok"] and web_demo_ok and video_ok,
        "external_submission_ok": False,
        "external_gates": EXTERNAL_GATES,
    }


def write_markdown(report: dict[str, Any], path: Path) -> None:
    lines = [
        "# Qdrant Reward Route Radar Preflight",
        "",
        f"Generated: `{report['generated_at']}`",
        f"Local OK: `{str(report['local_ok']).lower()}`",
        f"Qdrant client available: `{str(report['qdrant_client_available']).lower()}`",
        f"External submission OK: `{str(report['external_submission_ok']).lower()}`",
        f"Web demo OK: `{str(report['web_demo_ok']).lower()}`",
        f"Video OK: `{str(report['video_ok']).lower()}`",
        "",
        "## Demo Smoke",
        "",
        f"- ok: `{str(report['demo_smoke']['ok']).lower()}`",
        f"- indexed opportunities: `{report['demo_smoke'].get('indexed_opportunities', 0)}`",
        f"- route ids: `{', '.join(report['demo_smoke'].get('route_ids', []))}`",
        "",
        "## Missing Required Files",
        "",
    ]
    if report["missing_required_files"]:
        lines.extend(f"- `{item}`" for item in report["missing_required_files"])
    else:
        lines.append("- none")
    lines.extend(["", "## External Gates", ""])
    lines.extend(f"- {gate}" for gate in report["external_gates"])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    report = build_report()
    json_path = KIT_ROOT / "contest_preflight.json"
    md_path = KIT_ROOT / "contest_preflight.md"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown(report, md_path)
    print(json.dumps({"json": str(json_path), "markdown": str(md_path), "local_ok": report["local_ok"]}, sort_keys=True))
    return 0 if report["local_ok"] else 2


if __name__ == "__main__":
    raise SystemExit(main())

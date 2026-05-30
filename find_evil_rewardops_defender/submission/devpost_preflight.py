#!/usr/bin/env python3
"""FIND EVIL Devpost submission preflight.

This validates local, non-account requirements and clearly separates them from
external actions such as video upload, account use, and Devpost submission.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = ROOT / "out" / "devpost_preflight.json"
VIDEO_HOST_PATTERN = re.compile(r"https://(?:www\.)?(youtube\.com|youtu\.be|vimeo\.com|youku\.com)/", re.I)
VIDEO_METADATA_FILE = "submission/video_upload_metadata.json"
VIDEO_MAX_SECONDS = 300


REQUIRED_LOCAL_FILES = [
    "README.md",
    "LICENSE",
    "assets/rewardops-find-evil-guard-20260530.mp4",
    "assets/rewardops-find-evil-guard-20260530-contact-sheet.png",
    "docs/ARCHITECTURE.md",
    "docs/architecture.svg",
    "docs/EVIDENCE_DATASET.md",
    "docs/ACCURACY_REPORT.md",
    "submission/SUBMISSION_DRAFT.md",
    "submission/SCREENCAST_SCRIPT.md",
    "submission/VIDEO_UPLOAD_METADATA.md",
    "submission/VIDEO_CAPTIONS.srt",
    "submission/VIDEO_TRANSCRIPT.md",
    VIDEO_METADATA_FILE,
    "cases/find_evil_local_case.json",
    "out/find_evil_case_report.json",
    "out/find_evil_case_report.md",
    "out/submission_guard_manifest.json",
    "run_terminal_demo.sh",
]


def read_json(path: Path, fallback: Any) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return fallback


def check_local_files(root: Path) -> list[dict[str, Any]]:
    return [
        {
            "requirement": f"file:{rel}",
            "ok": (root / rel).is_file(),
            "evidence": rel,
        }
        for rel in REQUIRED_LOCAL_FILES
    ]


def check_video_package(root: Path) -> list[dict[str, Any]]:
    metadata = read_json(root / VIDEO_METADATA_FILE, {})
    source_asset = metadata.get("source_asset")
    caption_file = metadata.get("caption_file")
    transcript_file = metadata.get("transcript_file")
    duration = metadata.get("duration_seconds")
    max_allowed = metadata.get("max_allowed_seconds") or VIDEO_MAX_SECONDS
    has_audio = bool(metadata.get("has_audio"))
    audio_codec = metadata.get("audio_codec")
    audio_channels = metadata.get("audio_channels")
    try:
        duration_seconds = float(duration)
        max_allowed_seconds = min(float(max_allowed), float(VIDEO_MAX_SECONDS))
    except (TypeError, ValueError):
        duration_seconds = -1.0
        max_allowed_seconds = float(VIDEO_MAX_SECONDS)
    try:
        channel_count = int(audio_channels or 0)
    except (TypeError, ValueError):
        channel_count = 0

    return [
        {
            "requirement": "local_demo_video_metadata",
            "ok": metadata.get("schema") == "rewardops.find_evil.video_upload_metadata.v1",
            "evidence": VIDEO_METADATA_FILE,
        },
        {
            "requirement": "local_demo_video_asset",
            "ok": bool(source_asset) and (root / str(source_asset)).is_file(),
            "evidence": source_asset or "missing source_asset",
        },
        {
            "requirement": "local_demo_video_under_5_minutes",
            "ok": 0 < duration_seconds < max_allowed_seconds,
            "evidence": f"{duration} seconds",
        },
        {
            "requirement": "local_demo_video_has_audio",
            "ok": has_audio and bool(audio_codec) and channel_count > 0,
            "evidence": f"codec={audio_codec or 'missing'} channels={audio_channels or 'missing'}",
        },
        {
            "requirement": "local_demo_video_captions_ready",
            "ok": bool(caption_file) and (root / str(caption_file)).is_file(),
            "evidence": caption_file or "missing caption_file",
        },
        {
            "requirement": "local_demo_video_transcript_ready",
            "ok": bool(transcript_file) and (root / str(transcript_file)).is_file(),
            "evidence": transcript_file or "missing transcript_file",
        },
    ]


def build_preflight(root: Path, video_url: str | None = None) -> dict[str, Any]:
    local_file_checks = check_local_files(root)
    video_package_checks = check_video_package(root)
    case_report = read_json(root / "out" / "find_evil_case_report.json", {})
    case_score = case_report.get("score") or {}
    submission_guard = read_json(root / "out" / "submission_guard_manifest.json", {})
    video_ok = bool(video_url and VIDEO_HOST_PATTERN.search(video_url))
    checks = [
        *local_file_checks,
        *video_package_checks,
        {
            "requirement": "public_repo_url",
            "ok": True,
            "evidence": "https://github.com/xordanblu/rewardops-guard",
        },
        {
            "requirement": "mit_license",
            "ok": "MIT License" in (root / "LICENSE").read_text(encoding="utf-8", errors="ignore"),
            "evidence": "LICENSE",
        },
        {
            "requirement": "ground_truth_case_passes",
            "ok": bool(case_score.get("passes_ground_truth")),
            "evidence": "out/find_evil_case_report.json",
        },
        {
            "requirement": "no_case_false_positives",
            "ok": len(case_score.get("false_positive_events") or []) == 0,
            "evidence": "out/find_evil_case_report.json",
        },
        {
            "requirement": "no_case_false_negatives",
            "ok": len(case_score.get("false_negative_events") or []) == 0,
            "evidence": "out/find_evil_case_report.json",
        },
        {
            "requirement": "release_guard_ready",
            "ok": submission_guard.get("verdict") == "release_ready"
            and int(submission_guard.get("blocking_findings") or 0) == 0,
            "evidence": "out/submission_guard_manifest.json",
        },
        {
            "requirement": "youtube_vimeo_or_youku_video_url",
            "ok": video_ok,
            "evidence": video_url or "missing external video URL",
            "external_action_required": True,
        },
        {
            "requirement": "devpost_form_submission",
            "ok": False,
            "evidence": "not submitted by local preflight",
            "external_action_required": True,
        },
    ]
    blocking = [check for check in checks if not check["ok"]]
    external_blocking = [check for check in blocking if check.get("external_action_required")]
    local_blocking = [check for check in blocking if not check.get("external_action_required")]
    return {
        "schema": "rewardops.find_evil.devpost_preflight.v1",
        "status": "ready_for_external_submission" if not local_blocking else "local_blocked",
        "local_ok": not local_blocking,
        "external_submission_ok": not blocking,
        "checks": checks,
        "local_blocking": local_blocking,
        "external_blocking": external_blocking,
        "video_url": video_url,
        "next_external_actions": [
            "Upload the demo video to YouTube, Vimeo, or Youku and rerun this preflight with --video-url.",
            "Complete the Devpost FIND EVIL submission form using submission/SUBMISSION_DRAFT.md.",
        ],
    }


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Validate local FIND EVIL Devpost submission readiness.")
    p.add_argument("--root", type=Path, default=ROOT)
    p.add_argument("--video-url")
    p.add_argument("--json-output", type=Path, default=DEFAULT_OUT)
    return p


def main() -> int:
    args = parser().parse_args()
    preflight = build_preflight(args.root, args.video_url)
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(json.dumps(preflight, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "status": preflight["status"],
                "local_ok": preflight["local_ok"],
                "external_submission_ok": preflight["external_submission_ok"],
                "local_blocking": len(preflight["local_blocking"]),
                "external_blocking": len(preflight["external_blocking"]),
            }
        )
    )
    return 0 if preflight["local_ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

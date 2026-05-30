#!/usr/bin/env python3
"""Pre-publication guard for the RewardOps Defender submission package.

The guard is deliberately local and deterministic. It creates a file manifest,
detects release-blocking secret patterns, and records prompt-injection fixture
phrases separately so reviewers can see that hostile text is test data rather
than an instruction source.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
from typing import Any


IGNORE_DIRS = {".git", "__pycache__", ".pytest_cache"}
TEXT_SUFFIXES = {
    "",
    ".css",
    ".html",
    ".env",
    ".json",
    ".jsonl",
    ".key",
    ".md",
    ".pem",
    ".py",
    ".sh",
    ".svg",
    ".txt",
    ".yml",
    ".yaml",
}

SECRET_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("private_key", re.compile(r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----")),
    ("openai_api_key", re.compile(r"\bsk-(?:proj-)?[A-Za-z0-9_-]{20,}\b")),
    ("github_token", re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{20,}\b")),
    ("aws_access_key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    (
        "credential_assignment",
        re.compile(r"(?i)\b(api[_-]?key|secret|password|token)\s*[:=]\s*['\"]?[A-Za-z0-9_./+=-]{16,}"),
    ),
]

INJECTION_FIXTURE_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("ignore_instructions", re.compile(r"(?i)\bignore\b.{0,80}\binstructions\b")),
    ("system_prompt_request", re.compile(r"(?i)\bsystem prompt\b")),
    ("developer_instruction_request", re.compile(r"(?i)\bdeveloper instructions\b")),
    ("internal_instruction_request", re.compile(r"(?i)\bpaste internal\b")),
]


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def iter_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for path in root.rglob("*"):
        if any(part in IGNORE_DIRS for part in path.relative_to(root).parts):
            continue
        if path.is_file():
            files.append(path)
    return sorted(files, key=lambda item: item.relative_to(root).as_posix())


def read_text_for_scan(path: Path) -> str | None:
    if path.suffix.lower() not in TEXT_SUFFIXES:
        return None
    raw = path.read_bytes()
    if b"\x00" in raw:
        return None
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return None


def scan_text(relative_path: str, text: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    blocking: list[dict[str, Any]] = []
    fixtures: list[dict[str, Any]] = []
    for line_no, line in enumerate(text.splitlines(), start=1):
        for pattern_id, pattern in SECRET_PATTERNS:
            if pattern.search(line):
                blocking.append({"file": relative_path, "line": line_no, "pattern": pattern_id})
        for pattern_id, pattern in INJECTION_FIXTURE_PATTERNS:
            if pattern.search(line):
                fixtures.append({"file": relative_path, "line": line_no, "pattern": pattern_id})
    return blocking, fixtures


def build_manifest(root: Path) -> dict[str, Any]:
    root = root.resolve()
    files = iter_files(root)
    file_entries = []
    blocking_findings: list[dict[str, Any]] = []
    injection_fixtures: list[dict[str, Any]] = []
    scanned_text_files = 0

    for path in files:
        relative_path = path.relative_to(root).as_posix()
        file_entries.append({"path": relative_path, "bytes": path.stat().st_size, "sha256": file_sha256(path)})
        text = read_text_for_scan(path)
        if text is None:
            continue
        scanned_text_files += 1
        blocking, fixtures = scan_text(relative_path, text)
        blocking_findings.extend(blocking)
        injection_fixtures.extend(fixtures)

    verdict = "release_ready" if not blocking_findings else "blocked_secret_review_required"
    return {
        "schema": "rewardops.submission_guard.v1",
        "generated_at": now_iso(),
        "root": str(root),
        "verdict": verdict,
        "file_count": len(file_entries),
        "scanned_text_file_count": scanned_text_files,
        "total_bytes": sum(item["bytes"] for item in file_entries),
        "blocking_findings": blocking_findings,
        "injection_fixture_count": len(injection_fixtures),
        "injection_fixtures": injection_fixtures,
        "file_manifest": file_entries,
        "safe_boundaries": [
            "Release is blocked if private keys, API keys, GitHub tokens, AWS keys, or credential assignments are found.",
            "Prompt-injection phrases are recorded as fixtures, not executed as instructions.",
            "The guard does not make network calls, publish content, sign wallets, or submit forms.",
        ],
    }


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Build a local publication-safety manifest.")
    p.add_argument("--root", type=Path, default=Path("."))
    p.add_argument("--json-output", type=Path, required=True)
    return p


def main() -> int:
    args = parser().parse_args()
    manifest = build_manifest(args.root)
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "verdict": manifest["verdict"],
                "file_count": manifest["file_count"],
                "blocking_findings": len(manifest["blocking_findings"]),
                "injection_fixture_count": manifest["injection_fixture_count"],
            },
            sort_keys=True,
        )
    )
    return 0 if manifest["verdict"] == "release_ready" else 1


if __name__ == "__main__":
    raise SystemExit(main())

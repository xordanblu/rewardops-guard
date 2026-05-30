#!/usr/bin/env python3
"""Build a local, reviewable submission bundle for the FHIR contest route."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys
from typing import Any
import zipfile

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from rewardops_guard.delivery_kits.intersystems_fhir_agent_pack.contest_preflight import build_report


KIT_ROOT = Path(__file__).resolve().parent
DEFAULT_OUTPUT_ROOT = KIT_ROOT / "submission_bundle"

EXCLUDED_PARTS = {
    "__pycache__",
    "submission_bundle",
}
EXCLUDED_SUFFIXES = {
    ".pyc",
    ".pyo",
    ".DS_Store",
}
REQUIRED_BUNDLE_FILES = {
    "README.md",
    "SUBMISSION_DRAFT.md",
    "ARTICLE_DRAFT.md",
    "Dockerfile",
    "docker-compose.yml",
    "module.xml",
    "fhir_summary_agent.py",
    "demo_server.py",
    "contest_preflight.py",
    "contest_packet.py",
    "sample_patient_bundle.json",
    "demo_assets/care_brief_demo_desktop.png",
    "demo_assets/care_brief_demo_mobile.png",
    "src/cls/RewardOps/FHIR/CareBriefAgent.cls",
}
SUBMISSION_GATE = "HOLD_OPEN_EXCHANGE_SUBMISSION"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def should_include(path: Path) -> bool:
    relative = path.relative_to(KIT_ROOT)
    if any(part in EXCLUDED_PARTS for part in relative.parts):
        return False
    if path.name in EXCLUDED_SUFFIXES or path.suffix in EXCLUDED_SUFFIXES:
        return False
    return path.is_file()


def iter_bundle_files() -> list[Path]:
    return sorted(
        (path for path in KIT_ROOT.rglob("*") if should_include(path)),
        key=lambda item: item.relative_to(KIT_ROOT).as_posix(),
    )


def file_entry(path: Path) -> dict[str, Any]:
    data = path.read_bytes()
    return {
        "path": path.relative_to(KIT_ROOT).as_posix(),
        "bytes": len(data),
        "sha256": sha256_bytes(data),
    }


def display_path(path: Path) -> str:
    try:
        return path.relative_to(KIT_ROOT).as_posix()
    except ValueError:
        return str(path)


def build_bundle(output_root: Path = DEFAULT_OUTPUT_ROOT) -> dict[str, Any]:
    output_root.mkdir(parents=True, exist_ok=True)
    files = iter_bundle_files()
    entries = [file_entry(path) for path in files]
    paths = {entry["path"] for entry in entries}
    missing_required = sorted(REQUIRED_BUNDLE_FILES - paths)
    preflight = build_report()
    zip_path = output_root / "fhir_care_brief_agent_submission_bundle.zip"
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in files:
            archive.write(path, path.relative_to(KIT_ROOT).as_posix())
    zip_hash = sha256_bytes(zip_path.read_bytes())
    manifest = {
        "generated_at": now_iso(),
        "bundle_name": "fhir_care_brief_agent_submission_bundle",
        "zip_path": display_path(zip_path),
        "zip_sha256": zip_hash,
        "file_count": len(entries),
        "files": entries,
        "missing_required": missing_required,
        "local_ok": preflight["local_ok"] and not missing_required,
        "external_submission_ok": False,
        "submission_gate": SUBMISSION_GATE,
        "external_gates": preflight["external_blockers_before_contest_submission"],
        "side_effects": "local zip and manifest generation only; no account, upload, KYC, wallet, spend, or social action",
    }
    (output_root / "submission_bundle_manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    write_markdown(manifest, output_root / "submission_bundle_manifest.md")
    return manifest


def write_markdown(manifest: dict[str, Any], output_path: Path) -> None:
    lines = [
        "# FHIR Care Brief Agent Submission Bundle",
        "",
        f"Generated: {manifest['generated_at']}",
        f"Local OK: `{str(manifest['local_ok']).lower()}`",
        f"External submission OK: `{str(manifest['external_submission_ok']).lower()}`",
        f"Submission gate: `{manifest['submission_gate']}`",
        f"ZIP: `{manifest['zip_path']}`",
        f"ZIP SHA-256: `{manifest['zip_sha256']}`",
        f"File count: `{manifest['file_count']}`",
        "",
        "## External Gates",
        "",
    ]
    lines.extend(f"- {gate}" for gate in manifest["external_gates"])
    lines.extend(["", "## Required Missing Files", ""])
    if manifest["missing_required"]:
        lines.extend(f"- {path}" for path in manifest["missing_required"])
    else:
        lines.append("- none")
    lines.extend(["", "## Files", ""])
    lines.extend(f"- `{item['path']}` sha256={item['sha256']}" for item in manifest["files"])
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    args = parser.parse_args()
    manifest = build_bundle(args.output_root)
    print(
        json.dumps(
            {
                "local_ok": manifest["local_ok"],
                "zip_path": manifest["zip_path"],
                "zip_sha256": manifest["zip_sha256"],
                "file_count": manifest["file_count"],
            },
            sort_keys=True,
        )
    )
    return 0 if manifest["local_ok"] else 2


if __name__ == "__main__":
    raise SystemExit(main())

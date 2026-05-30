from __future__ import annotations

import hashlib
import html
import json
import shutil
import zipfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_ROOT = ROOT.parent / "rewardops_guard_public_submission"

INCLUDE_ROOTS = (
    "rewardops_guard",
    "safety_gate",
    "find_evil_rewardops_defender",
)
INCLUDE_TOP_LEVEL = (
    "README.md",
    "PUBLIC_SUBMISSION_README.md",
    "index.html",
    ".nojekyll",
)
EXCLUDED_PARTS = {
    ".git",
    ".github",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    "node_modules",
}
EXCLUDED_SUFFIXES = {
    ".pyc",
    ".pyo",
    ".DS_Store",
}
EXCLUDED_BY_POLICY = [
    "secrets and account configs",
    "raw external task prompt archives",
    "wallet keys or signing material",
    "social/KYC/payment setup artifacts",
]
PUBLIC_LINKS = {
    "repository": "https://github.com/xordanx/rewardops-guard",
    "dashboard": "https://xordanx.github.io/rewardops-guard/",
    "find_evil_demo_video": (
        "https://xordanx.github.io/rewardops-guard/"
        "find_evil_rewardops_defender/assets/rewardops-find-evil-guard-20260530.mp4"
    ),
    "find_evil_contact_sheet": (
        "https://xordanx.github.io/rewardops-guard/"
        "find_evil_rewardops_defender/assets/"
        "rewardops-find-evil-guard-20260530-contact-sheet.png"
    ),
}
WALLET_OR_KEY_BLOCKLIST = (
    "0xEAF9f10F8ff6c5175" + "B87A0aDd982Fa2BE83366FB",
    "0x7b582985b30971b164" + "e00b8e5124b120dc187dd6",
    "0xa6904E2F73b1837d6c" + "07037A743D3E5Fed363AE3",
    "-----BEGIN " + "PRIVATE KEY-----",
    "-----BEGIN OPENSSH " + "PRIVATE KEY-----",
)


def read_json(path: Path, default: dict[str, Any]) -> dict[str, Any]:
    try:
        return json.loads(path.read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def is_excluded(path: Path) -> bool:
    if any(part in EXCLUDED_PARTS for part in path.parts):
        return True
    return path.name in EXCLUDED_SUFFIXES or path.suffix in EXCLUDED_SUFFIXES


def iter_public_files() -> list[Path]:
    files: list[Path] = []
    for rel in INCLUDE_TOP_LEVEL:
        path = ROOT / rel
        if path.is_file() and not is_excluded(path.relative_to(ROOT)):
            files.append(path)

    for rel_root in INCLUDE_ROOTS:
        base = ROOT / rel_root
        if not base.exists():
            continue
        for path in sorted(base.rglob("*")):
            rel = path.relative_to(ROOT)
            if path.is_file() and not is_excluded(rel):
                files.append(path)

    return sorted(set(files), key=lambda p: p.relative_to(ROOT).as_posix())


def detect_blocked_public_secrets(files: list[Path]) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    for path in files:
        try:
            text = path.read_text(errors="ignore")
        except UnicodeDecodeError:
            continue
        for marker in WALLET_OR_KEY_BLOCKLIST:
            if marker in text:
                findings.append(
                    {
                        "path": path.relative_to(ROOT).as_posix(),
                        "marker": marker[:10] + "...",
                    }
                )
    return findings


def money_snapshot() -> dict[str, float]:
    revenue = read_json(ROOT / "rewardops_guard" / "revenue_evidence_pack.json", {})
    return {
        "confirmed_revenue_usd": float(revenue.get("confirmed_revenue_usd") or 0.0),
        "pending_submission_usd": float(revenue.get("pending_submission_usd") or 0.0),
        "submitted_pending_verification_usd": float(
            revenue.get("submitted_pending_verification_usd") or 0.0
        ),
        "inbound_market_surface_usd": float(
            revenue.get("inbound_market_surface_usd") or 0.0
        ),
    }


def write_public_readme(generated_at: str, files: list[dict[str, Any]], money: dict[str, float]) -> None:
    lines = [
        "# RewardOps Guard Public Submission Bundle",
        "",
        f"Generated: {generated_at}",
        "",
        "## Purpose",
        "",
        "This bundle contains a sanitized local demo and evidence pack for public",
        "hackathon review, buyer diligence, or repository publication.",
        "",
        "## Public Review Links",
        "",
        f"- Repository: {PUBLIC_LINKS['repository']}",
        f"- Dashboard: {PUBLIC_LINKS['dashboard']}",
        f"- FIND EVIL demo video: {PUBLIC_LINKS['find_evil_demo_video']}",
        f"- FIND EVIL contact sheet: {PUBLIC_LINKS['find_evil_contact_sheet']}",
        "",
        "## Safety Boundary",
        "",
        "- No Devpost/forum/contest submission was performed by this bundle.",
        "- No account creation, KYC, social posting, wallet signing, or spend action was performed.",
        "- Raw external task prompts and private credentials are intentionally excluded.",
        "- Money is counted only when spendable or visibly settled.",
        "",
        "## Current Money Evidence",
        "",
        f"- Confirmed revenue: ${money['confirmed_revenue_usd']:.2f}",
        f"- Pending ClawMoney submissions: ${money['pending_submission_usd']:.2f}",
        "- Submitted pending verification after failed-audit adjustment: "
        f"${money['submitted_pending_verification_usd']:.2f}",
        f"- Inbound market surface: ${money['inbound_market_surface_usd']:.2f}",
        "",
        "## Verification",
        "",
        "Run from the repository root:",
        "",
        "```bash",
        "python3 -m unittest discover -s . -p 'test_*.py' -v",
        "python3 -m unittest discover -s rewardops_guard -p 'test_*.py' -v",
        "python3 rewardops_guard/build_dashboard.py",
        "python3 rewardops_guard/public_submission_bundle.py",
        "```",
        "",
        "## Files",
        "",
    ]
    lines.extend(
        f"- `{item['path']}` sha256={item['sha256']}" for item in files if item["ok"]
    )
    content = "\n".join(lines) + "\n"
    (ROOT / "PUBLIC_SUBMISSION_README.md").write_text(content)
    (ROOT / "README.md").write_text(content)


def write_single_html(bundle_dir: Path, html_path: Path, manifest: dict[str, Any]) -> None:
    rows = "\n".join(
        "<tr>"
        f"<td>{html.escape(item['path'])}</td>"
        f"<td>{item['bytes']}</td>"
        f"<td><code>{item['sha256']}</code></td>"
        "</tr>"
        for item in manifest["files"]
    )
    content = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>RewardOps Guard Public Submission</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; margin: 32px; color: #111827; }}
    table {{ border-collapse: collapse; width: 100%; font-size: 13px; }}
    th, td {{ border: 1px solid #d1d5db; padding: 8px; text-align: left; vertical-align: top; }}
    th {{ background: #f3f4f6; }}
    code {{ white-space: nowrap; }}
  </style>
</head>
<body>
  <h1>RewardOps Guard Public Submission</h1>
  <p>Generated: {html.escape(manifest["generated_at"])}</p>
  <p>Submission gate: <strong>{html.escape(manifest["submission_gate"])}</strong></p>
  <h2>Public Review Links</h2>
  <ul>
    <li>Repository: <a href="{html.escape(PUBLIC_LINKS["repository"])}">{html.escape(PUBLIC_LINKS["repository"])}</a></li>
    <li>Dashboard: <a href="{html.escape(PUBLIC_LINKS["dashboard"])}">{html.escape(PUBLIC_LINKS["dashboard"])}</a></li>
    <li>FIND EVIL demo video: <a href="{html.escape(PUBLIC_LINKS["find_evil_demo_video"])}">{html.escape(PUBLIC_LINKS["find_evil_demo_video"])}</a></li>
    <li>FIND EVIL contact sheet: <a href="{html.escape(PUBLIC_LINKS["find_evil_contact_sheet"])}">{html.escape(PUBLIC_LINKS["find_evil_contact_sheet"])}</a></li>
  </ul>
  <h2>Money Evidence</h2>
  <ul>
    <li>Confirmed revenue: ${manifest["money"]["confirmed_revenue_usd"]:.2f}</li>
    <li>Pending submissions: ${manifest["money"]["pending_submission_usd"]:.2f}</li>
    <li>Submitted pending verification: ${manifest["money"]["submitted_pending_verification_usd"]:.2f}</li>
    <li>Inbound market surface: ${manifest["money"]["inbound_market_surface_usd"]:.2f}</li>
  </ul>
  <h2>Safety Boundary</h2>
  <ul>
    <li>No Devpost/forum/contest submission, social post, signing, spend, KYC, or account action was performed.</li>
    <li>Private credentials, raw prompts, and signing material are excluded.</li>
  </ul>
  <h2>Files</h2>
  <table>
    <thead><tr><th>Path</th><th>Bytes</th><th>SHA-256</th></tr></thead>
    <tbody>{rows}</tbody>
  </table>
  <p>Bundle directory: <code>{html.escape(bundle_dir.name)}</code></p>
</body>
</html>
"""
    html_path.write_text(content)


def build_bundle() -> dict[str, Any]:
    generated_at = datetime.now(UTC).replace(microsecond=0).isoformat()
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%S%fZ")
    bundle_name = f"bundle_{stamp}"
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    bundle_dir = OUTPUT_ROOT / bundle_name
    bundle_dir.mkdir()

    public_files = iter_public_files()
    blocked = detect_blocked_public_secrets(public_files)
    money = money_snapshot()
    file_entries: list[dict[str, Any]] = []

    for source in public_files:
        rel = source.relative_to(ROOT).as_posix()
        data = source.read_bytes()
        target = bundle_dir / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        file_entries.append(
            {
                "path": rel,
                "bytes": len(data),
                "sha256": sha256_bytes(data),
                "ok": True,
            }
        )

    write_public_readme(generated_at, file_entries, money)
    for readme_source in (ROOT / "PUBLIC_SUBMISSION_README.md", ROOT / "README.md"):
        readme_rel = readme_source.relative_to(ROOT).as_posix()
        readme_data = readme_source.read_bytes()
        shutil.copy2(readme_source, bundle_dir / readme_rel)
        for item in file_entries:
            if item["path"] == readme_rel:
                item["bytes"] = len(readme_data)
                item["sha256"] = sha256_bytes(readme_data)
                break

    manifest = {
        "ok": not blocked,
        "generated_at": generated_at,
        "bundle_dir": bundle_name,
        "file_count": len(file_entries),
        "files": file_entries,
        "money": money,
        "submission_gate": "HOLD_PUBLIC_SUBMISSION",
        "external_actions_performed": [],
        "public_links": PUBLIC_LINKS,
        "excluded_by_policy": EXCLUDED_BY_POLICY,
        "missing_or_blocked": blocked,
        "zip_path": f"{bundle_name}.zip",
        "single_html_path": f"{bundle_name}.html",
    }

    manifest_json = json.dumps(manifest, indent=2, sort_keys=True) + "\n"
    manifest["manifest_sha256"] = sha256_bytes(manifest_json.encode())
    manifest_json = json.dumps(manifest, indent=2, sort_keys=True) + "\n"
    (bundle_dir / "manifest.json").write_text(manifest_json)
    (ROOT / "manifest.json").write_text(manifest_json)
    (OUTPUT_ROOT / "latest.json").write_text(manifest_json)

    zip_path = OUTPUT_ROOT / manifest["zip_path"]
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(bundle_dir.rglob("*")):
            if path.is_file():
                archive.write(path, path.relative_to(bundle_dir))
    zip_sha = sha256_bytes(zip_path.read_bytes())
    manifest["zip_sha256"] = zip_sha
    manifest_json = json.dumps(manifest, indent=2, sort_keys=True) + "\n"
    (bundle_dir / "manifest.json").write_text(manifest_json)
    (ROOT / "manifest.json").write_text(manifest_json)
    (OUTPUT_ROOT / "latest.json").write_text(manifest_json)

    html_path = OUTPUT_ROOT / manifest["single_html_path"]
    write_single_html(bundle_dir, html_path, manifest)
    (OUTPUT_ROOT / "latest.md").write_text(
        "\n".join(
            [
                "# RewardOps Guard Public Submission",
                "",
                f"- Generated: {manifest['generated_at']}",
                f"- Bundle: `{bundle_dir}`",
                f"- ZIP: `{zip_path}`",
                f"- Single HTML: `{html_path}`",
                f"- Submission gate: `{manifest['submission_gate']}`",
                f"- Confirmed revenue: ${money['confirmed_revenue_usd']:.2f}",
                f"- Pending submissions: ${money['pending_submission_usd']:.2f}",
            ]
        )
        + "\n"
    )
    return manifest | {
        "bundle_path": str(bundle_dir),
        "zip_abs_path": str(zip_path),
        "single_html_abs_path": str(html_path),
    }


def main() -> None:
    print(json.dumps(build_bundle(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

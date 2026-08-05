#!/usr/bin/env python3
"""Fail if a release tag is not ready for public publication."""

from __future__ import annotations

import argparse
import re
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_BY_MAJOR_MINOR = {
    "0.6": ROOT / "docs" / "acceptance" / "release-gate-0.6.toml",
    "0.7": ROOT / "docs" / "acceptance" / "release-gate-0.7.toml",
    "0.8": ROOT / "docs" / "acceptance" / "release-gate-0.8.toml",
    "0.9": ROOT / "docs" / "acceptance" / "release-gate-0.9.toml",
    "0.10": ROOT / "docs" / "acceptance" / "release-gate-0.10.toml",
    "0.11": ROOT / "docs" / "acceptance" / "release-gate-0.11.toml",
    "0.12": ROOT / "docs" / "acceptance" / "release-gate-0.12.toml",
}
DEFAULT_EVIDENCE = EVIDENCE_BY_MAJOR_MINOR["0.6"]


def evidence_manifest_for(version: str) -> Path:
    parts = version.split(".")
    if len(parts) >= 2:
        key = f"{parts[0]}.{parts[1]}"
        if key in EVIDENCE_BY_MAJOR_MINOR:
            return EVIDENCE_BY_MAJOR_MINOR[key]
    return DEFAULT_EVIDENCE


def _is_alpha_package(project: dict[str, object]) -> bool:
    classifiers = project.get("classifiers")
    if not isinstance(classifiers, list):
        return False
    return any("Development Status :: 3 - Alpha" in str(c) for c in classifiers)


def check_packages(tag_version: str) -> list[str]:
    errors: list[str] = []
    if not (ROOT / "LICENSE").is_file():
        errors.append("missing root LICENSE (required before public publication)")

    for pyproject in sorted((ROOT / "packages").glob("*/pyproject.toml")):
        data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
        project = data["project"]
        name = str(project["name"])
        version = str(project["version"])
        alpha = _is_alpha_package(project)
        # Alpha satellites version independently of the Beta flagship train.
        expected = version if alpha else tag_version
        if not alpha and version != tag_version:
            errors.append(f"{name}: package version {version!r} != tag {tag_version!r}")
        if "license" not in project and "license-files" not in project:
            errors.append(f"{name}: [project].license (or license-files) is required")
        pkg_dir = pyproject.parent
        init = next(pkg_dir.glob("src/*/__init__.py"))
        init_text = init.read_text(encoding="utf-8")
        match = re.search(r'^__version__\s*=\s*["\']([^"\']+)["\']', init_text, re.M)
        if not match:
            errors.append(f"{name}: __version__ not found in {init}")
        elif match.group(1) != expected:
            errors.append(f"{name}: __version__ {match.group(1)!r} != package {expected!r}")
        changelog = pkg_dir / "CHANGELOG.md"
        if not changelog.is_file():
            errors.append(f"{name}: missing CHANGELOG.md")
        elif f"[{expected}]" not in changelog.read_text(encoding="utf-8"):
            errors.append(f"{name}: CHANGELOG.md lacks [{expected}] section")
    return errors


def check_evidence_manifest(path: Path) -> list[str]:
    errors: list[str] = []
    if not path.is_file():
        return [f"missing evidence manifest: {path}"]
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    rows = data.get("evidence")
    if not isinstance(rows, list) or not rows:
        return [f"{path}: [[evidence]] entries required"]
    seen: set[str] = set()
    for row in rows:
        if not isinstance(row, dict):
            errors.append(f"{path}: evidence row must be a table")
            continue
        eid = str(row.get("id", "")).strip()
        state = str(row.get("state", "")).strip()
        command = str(row.get("command", "")).strip()
        owner = str(row.get("owner", "")).strip()
        if not eid:
            errors.append(f"{path}: evidence id is required")
            continue
        if eid in seen:
            errors.append(f"{path}: duplicate evidence id {eid}")
        seen.add(eid)
        if state not in {"Planned", "Implemented", "Verified", "Deferred", "Blocked"}:
            errors.append(f"{eid}: invalid state {state!r}")
        if not owner:
            errors.append(f"{eid}: owner is required")
        if state == "Verified" and not command:
            errors.append(f"{eid}: Verified entries require a named command")
        if state == "Deferred":
            if not str(row.get("rationale", "")).strip():
                errors.append(f"{eid}: Deferred entries require rationale")
            if not str(row.get("destination", "")).strip():
                errors.append(f"{eid}: Deferred entries require destination")
        if state in {"Blocked", "Implemented", "Planned"}:
            errors.append(
                f"{eid}: state {state!r} does not close the release gate "
                "(use Verified or Deferred with ownership)"
            )
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("version", help="Package version without the leading v")
    parser.add_argument(
        "--evidence-manifest",
        type=Path,
        default=None,
        help="Path to release-gate evidence TOML (default: version-selected manifest)",
    )
    parser.add_argument(
        "--allow-planned",
        action="store_true",
        help="Accept Planned/Implemented rows (scaffold / in-progress gates)",
    )
    parser.add_argument(
        "--skip-evidence",
        action="store_true",
        help="Skip evidence manifest checks (metadata-only)",
    )
    args = parser.parse_args()
    errors = check_packages(args.version)
    if not args.skip_evidence:
        manifest = args.evidence_manifest or evidence_manifest_for(args.version)
        if args.allow_planned:
            errors.extend(check_evidence_manifest_lenient(manifest))
        else:
            errors.extend(check_evidence_manifest(manifest))
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(f"ok: release gate for {args.version}")
    return 0


def check_evidence_manifest_lenient(path: Path) -> list[str]:
    """Validate shape without requiring Verified/Deferred closure."""
    errors: list[str] = []
    if not path.is_file():
        return [f"missing evidence manifest: {path}"]
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    rows = data.get("evidence")
    if not isinstance(rows, list) or not rows:
        return [f"{path}: [[evidence]] entries required"]
    seen: set[str] = set()
    for row in rows:
        if not isinstance(row, dict):
            errors.append(f"{path}: evidence row must be a table")
            continue
        eid = str(row.get("id", "")).strip()
        state = str(row.get("state", "")).strip()
        owner = str(row.get("owner", "")).strip()
        if not eid:
            errors.append(f"{path}: evidence id is required")
            continue
        if eid in seen:
            errors.append(f"{path}: duplicate evidence id {eid}")
        seen.add(eid)
        if state not in {"Planned", "Implemented", "Verified", "Deferred", "Blocked"}:
            errors.append(f"{eid}: invalid state {state!r}")
        if not owner:
            errors.append(f"{eid}: owner is required")
        if state == "Verified" and not str(row.get("command", "")).strip():
            errors.append(f"{eid}: Verified entries require a named command")
        if state == "Deferred":
            if not str(row.get("rationale", "")).strip():
                errors.append(f"{eid}: Deferred entries require rationale")
            if not str(row.get("destination", "")).strip():
                errors.append(f"{eid}: Deferred entries require destination")
    return errors


if __name__ == "__main__":
    raise SystemExit(main())

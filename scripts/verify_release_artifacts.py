#!/usr/bin/env python3
"""Verify release-built artifacts against the approved reproducible candidate hashes."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.verify_release_reproducibility import (  # noqa: E402
    artifact_inventory,
    expected_packages,
    phase_for_version,
    validate_python310_evidence_data,
    validate_upgrade_rollback_evidence_data,
)

EVIDENCE = ROOT / "docs/acceptance/compatibility-report-100/local-build-evidence.json"
DIST = ROOT / "dist"
EVIDENCE_ONLY_PATHS = {
    "docs/acceptance/compatibility-report-100/README.md",
    "docs/acceptance/compatibility-report-100/edron-build-evidence.json",
    "docs/acceptance/compatibility-report-100/local-bridge.json",
    "docs/acceptance/compatibility-report-100/local-build-evidence.json",
    "docs/acceptance/compatibility-report-100/verification-100.json",
}
PHASE_130_EVIDENCE_ONLY_PATHS = {
    "docs/acceptance/RELEASE_1_3.md",
    "docs/acceptance/release-gate-1.3.toml",
}


def evidence_source_errors(
    source_commit: object,
    *,
    evidence_root: Path | None = None,
) -> list[str]:
    """Return errors when an approved ledger no longer describes this checkout."""
    if not isinstance(source_commit, str) or len(source_commit) != 40:
        return ["approved release evidence source_commit must be a full commit hash"]
    try:
        changed = subprocess.check_output(
            ["git", "diff", "--name-only", f"{source_commit}..HEAD"],
            cwd=ROOT,
            text=True,
            stderr=subprocess.STDOUT,
        ).splitlines()
        working_tree_changed = subprocess.check_output(
            ["git", "diff", "--name-only", "HEAD", "--"],
            cwd=ROOT,
            text=True,
            stderr=subprocess.STDOUT,
        ).splitlines()
        untracked = subprocess.check_output(
            ["git", "ls-files", "--others", "--exclude-standard"],
            cwd=ROOT,
            text=True,
            stderr=subprocess.STDOUT,
        ).splitlines()
    except (OSError, subprocess.CalledProcessError):
        return ["approved release evidence source_commit is unavailable in this checkout"]
    allowed_paths = set(EVIDENCE_ONLY_PATHS)
    allowed_prefixes: tuple[str, ...] = ()
    if evidence_root is not None:
        try:
            relative_root = evidence_root.resolve().relative_to(ROOT.resolve()).as_posix()
            allowed_prefix = relative_root.rstrip("/") + "/"
        except ValueError:
            return ["approved release evidence directory must be inside the repository"]
        allowed_paths = {
            allowed_prefix + "python-artifacts.json",
            allowed_prefix + "native-artifacts.json",
            allowed_prefix + "python310-compatibility.json",
            allowed_prefix + "upgrade-rollback-1.2.json",
            allowed_prefix + "upgrade-rollback-1.3.json",
        }
        if relative_root == "docs/acceptance/evidence-130":
            allowed_paths.update(PHASE_130_EVIDENCE_ONLY_PATHS)
            allowed_prefixes = (allowed_prefix,)
    unexpected = sorted(
        path
        for path in set(changed) | set(working_tree_changed) | set(untracked)
        if path not in allowed_paths and not path.startswith(allowed_prefixes)
    )
    if unexpected:
        return [
            "approved release evidence is stale; source_commit predates non-evidence changes: "
            + ", ".join(unexpected[:5])
        ]
    return []


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence-manifest", type=Path, default=EVIDENCE)
    parser.add_argument("--dist-dir", type=Path, default=DIST)
    parser.add_argument("--expected-artifact-count", type=int, default=None)
    parser.add_argument(
        "--exact-set",
        action="store_true",
        help="Reject any wheel or sdist not included in the approved artifact ledger",
    )
    args = parser.parse_args(argv if argv is not None else [])
    evidence_path = args.evidence_manifest.resolve()
    dist_dir = args.dist_dir.resolve()
    errors: list[str] = []
    try:
        evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"unable to read approved artifact ledger: {exc}", file=sys.stderr)
        return 1
    if not isinstance(evidence, dict):
        print("approved artifact ledger must contain a JSON object", file=sys.stderr)
        return 1
    artifact_rows = evidence.get("artifacts", [])
    if not isinstance(artifact_rows, list):
        print("approved artifact ledger must contain an artifacts list", file=sys.stderr)
        return 1
    expected = {
        str(item["name"]): str(item["sha256"])
        for item in artifact_rows
        if isinstance(item, dict) and item.get("name") and item.get("sha256")
    }
    evidence_root = evidence_path.parent if evidence_path != EVIDENCE.resolve() else None
    errors.extend(
        evidence_source_errors(evidence.get("source_commit"), evidence_root=evidence_root)
    )
    try:
        current_packages = expected_packages() if evidence_root is not None else {}
    except (OSError, ValueError) as exc:
        current_packages = {}
        errors.append(f"unable to read current release package inventory: {exc}")
    expected_artifact_count = args.expected_artifact_count
    if expected_artifact_count is None:
        expected_artifact_count = len(current_packages) * 2 if evidence_root is not None else 26
    if expected_artifact_count < 1:
        errors.append("expected artifact count must be positive")
    if len(expected) != expected_artifact_count:
        errors.append(
            f"approved artifact count must be {expected_artifact_count}, found {len(expected)}"
        )
    if len(expected) != len(artifact_rows):
        errors.append("approved artifact ledger contains missing names or duplicate artifact names")
    if evidence_root is not None:
        target = evidence.get("target")
        predecessor_version = evidence.get("predecessor_version")
        try:
            target_version = str(target).removeprefix("v")
            phase, phase_code = phase_for_version(target_version)
        except ValueError as exc:
            errors.append(f"approved artifact ledger has an invalid release target: {exc}")
            phase, phase_code, target_version = "", "", ""
        if evidence.get("schema") != f"hedron.phase-{phase_code}-python-artifact-evidence/1":
            errors.append("approved artifact ledger has an invalid phase schema")
        if evidence.get("phase") != phase or evidence.get("target") != f"v{target_version}":
            errors.append("approved artifact ledger has an invalid release target")
        if not isinstance(predecessor_version, str) or not predecessor_version:
            predecessor_version = "1.1.3" if phase == "1.2" else ""
        expected_predecessor = "1.1.3" if phase == "1.2" else "1.2.0"
        if predecessor_version != expected_predecessor:
            errors.append(f"approved {phase} artifact ledger has an invalid predecessor")
        reproducibility = evidence.get("reproducibility")
        if (
            not isinstance(reproducibility, dict)
            or reproducibility.get("verified") is not True
            or reproducibility.get("repeat_builds") != 2
        ):
            errors.append("approved artifact ledger lacks two verified reproducible builds")
        packages = evidence.get("packages")
        if (
            not isinstance(packages, list)
            or not all(isinstance(name, str) for name in packages)
            or len(packages) * 2 != expected_artifact_count
            or len(set(packages)) != len(packages)
            or "hedron-native" in packages
        ):
            errors.append("approved artifact ledger has an invalid Python package inventory")
        else:
            try:
                if packages != list(current_packages):
                    errors.append("approved artifact ledger package order is stale or incomplete")
                built = artifact_inventory(dist_dir, current_packages)
                if set(expected) != set(built):
                    errors.append(
                        "approved artifact ledger does not cover the exact current wheel/sdist set"
                    )
                try:
                    validate_python310_evidence_data(
                        evidence.get("python310_compatibility"),
                        source_commit=str(evidence.get("source_commit", "")),
                        artifacts=artifact_rows,
                        candidate_version=current_packages["hedron"],
                        predecessor_version=predecessor_version,
                    )
                except ValueError as exc:
                    errors.append(
                        f"approved {phase} artifact ledger lacks valid Python 3.10 evidence: {exc}"
                    )
                try:
                    validate_upgrade_rollback_evidence_data(
                        evidence.get("installed_application_upgrade_rollback"),
                        source_commit=str(evidence.get("source_commit", "")),
                        artifacts=artifact_rows,
                        predecessor_version=predecessor_version,
                        candidate_version=current_packages["hedron"],
                    )
                except ValueError as exc:
                    errors.append(
                        f"approved {phase} artifact ledger lacks valid "
                        f"upgrade/rollback evidence: {exc}"
                    )
            except (OSError, ValueError) as exc:
                errors.append(f"unable to verify current package artifact inventory: {exc}")
        if not str(evidence.get("retention_reference", "")).strip():
            errors.append("approved artifact ledger must identify retained build artifacts")
        environment = evidence.get("environment")
        if (
            not isinstance(environment, dict)
            or not all(
                str(environment.get(key, "")).strip()
                for key in ("python", "uv", "os", "architecture")
            )
            or environment.get("source_date_epoch") != 315619200
        ):
            errors.append("approved artifact ledger lacks its reproducible build environment")
    for name, digest in expected.items():
        if len(digest) != 64 or any(char not in "0123456789abcdef" for char in digest):
            errors.append(f"{name}: invalid SHA-256 digest in approved ledger")
    for name, digest in sorted(expected.items()):
        path = dist_dir / name
        if not path.is_file():
            errors.append(f"missing approved release artifact: {name}")
            continue
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != digest:
            errors.append(f"{name}: approved sha256={digest}, release build sha256={actual}")
        if evidence_root is not None:
            row = next(
                item
                for item in artifact_rows
                if isinstance(item, dict) and item.get("name") == name
            )
            if row.get("size") != path.stat().st_size:
                errors.append(f"{name}: approved artifact size does not match release build")
    if args.exact_set:
        built = {
            path.name
            for pattern in ("*.whl", "*.tar.gz")
            for path in dist_dir.glob(pattern)
            if path.is_file()
        }
        unapproved = sorted(built - set(expected))
        if unapproved:
            errors.append("unapproved release artifacts present: " + ", ".join(unapproved[:5]))
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(f"ok: release build matches {len(expected)} approved artifact hashes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

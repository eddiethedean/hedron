#!/usr/bin/env python3
"""Compare two complete 1.2/1.3 Python release builds and write their hash ledger."""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import subprocess
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NATIVE_PACKAGE = "hedron-native"
PREDECESSOR_VERSION = "1.1.3"


def phase_for_version(version: str) -> tuple[str, str]:
    parts = version.split(".")
    if len(parts) != 3 or any(not part.isdigit() for part in parts):
        raise ValueError(f"invalid release version: {version!r}")
    phase = ".".join(parts[:2])
    if phase not in {"1.2", "1.3"}:
        raise ValueError(f"unsupported reproducible release phase: {version!r}")
    return phase, phase.replace(".", "") + "0"


def predecessor_for_version(version: str) -> str:
    phase, _phase_code = phase_for_version(version)
    return "1.1.3" if phase == "1.2" else "1.2.0"


def expected_packages() -> dict[str, str]:
    order_data = tomllib.loads((ROOT / "release/publish-order.toml").read_text(encoding="utf-8"))
    order = order_data.get("order")
    if not isinstance(order, list) or not all(isinstance(name, str) for name in order):
        raise ValueError("release/publish-order.toml must define a package order")
    projects: dict[str, str] = {}
    for path in (ROOT / "packages").glob("*/pyproject.toml"):
        project = tomllib.loads(path.read_text(encoding="utf-8")).get("project", {})
        if isinstance(project, dict) and isinstance(project.get("name"), str):
            projects[project["name"]] = str(project.get("version", ""))
    missing = sorted(set(projects) - set(order))
    unknown = sorted(set(order) - set(projects))
    if missing or unknown:
        raise ValueError(f"publish order mismatch: missing={missing}, unknown={unknown}")
    return {name: projects[name] for name in order if name != NATIVE_PACKAGE}


def artifact_inventory(directory: Path, packages: dict[str, str]) -> dict[str, str]:
    files = {
        path.name: hashlib.sha256(path.read_bytes()).hexdigest()
        for pattern in ("*.whl", "*.tar.gz")
        for path in directory.glob(pattern)
        if path.is_file()
    }
    expected_names: set[str] = set()
    errors: list[str] = []
    for name, version in packages.items():
        normalized = name.replace("-", "_")
        wheel_names = [
            filename
            for filename in files
            if filename.startswith(f"{normalized}-{version}-") and filename.endswith(".whl")
        ]
        sdist_name = f"{normalized}-{version}.tar.gz"
        if len(wheel_names) != 1:
            errors.append(f"{name}: expected one {version} wheel, found {wheel_names}")
        if sdist_name not in files:
            errors.append(f"{name}: missing {version} source distribution {sdist_name}")
        expected_names.update(wheel_names)
        if sdist_name in files:
            expected_names.add(sdist_name)
    extras = sorted(set(files) - expected_names)
    if extras:
        errors.append("unexpected release artifacts: " + ", ".join(extras[:8]))
    if errors:
        raise ValueError("\n".join(errors))
    return files


def compare_builds(
    first_dir: Path,
    second_dir: Path,
    *,
    packages: dict[str, str],
) -> list[dict[str, str | int]]:
    first = artifact_inventory(first_dir, packages)
    second = artifact_inventory(second_dir, packages)
    if set(first) != set(second):
        raise ValueError(
            f"reproducible artifact inventories differ: "
            f"first-only={sorted(set(first) - set(second))}, "
            f"second-only={sorted(set(second) - set(first))}"
        )
    mismatched = sorted(name for name in first if first[name] != second[name])
    if mismatched:
        raise ValueError("non-reproducible artifact hashes: " + ", ".join(mismatched[:8]))
    return [
        {
            "name": name,
            "sha256": digest,
            "size": (first_dir / name).stat().st_size,
        }
        for name, digest in sorted(first.items())
    ]


def validate_python310_evidence_data(
    evidence: object,
    *,
    source_commit: str,
    artifacts: list[dict[str, str | int]],
    candidate_version: str,
    predecessor_version: str = PREDECESSOR_VERSION,
) -> dict[str, object]:
    if not isinstance(evidence, dict):
        raise ValueError("Python 3.10 compatibility evidence must be a JSON object")
    _phase, phase_code = phase_for_version(candidate_version)
    if (
        evidence.get("schema") != f"hedron.phase-{phase_code}-python310-compatibility/1"
        or evidence.get("source_commit") != source_commit
        or evidence.get("candidate_install") != "rejected by Requires-Python"
        or evidence.get("candidate_rejection_mentions_python_310_and_311") is not True
        or evidence.get("unpinned_requirement") != "hedron"
        or evidence.get("resolved_version") != predecessor_version
        or evidence.get("predecessor_version") != predecessor_version
        or not str(evidence.get("python", "")).startswith("3.10.")
        or evidence.get("platform") in (None, "")
        or evidence.get("architecture") in (None, "")
    ):
        raise ValueError("Python 3.10 compatibility evidence is incomplete or mismatched")
    candidate_name = evidence.get("candidate_artifact")
    candidate_hash = evidence.get("candidate_sha256")
    if not isinstance(candidate_name, str) or not candidate_name.startswith(
        f"hedron-{candidate_version}-"
    ):
        raise ValueError("Python 3.10 compatibility evidence names the wrong candidate wheel")
    candidate = next((row for row in artifacts if row["name"] == candidate_name), None)
    if candidate is None or candidate.get("sha256") != candidate_hash:
        raise ValueError("Python 3.10 compatibility evidence is not bound to the Hedron wheel")
    return evidence


def validate_python310_evidence(
    evidence_path: Path,
    *,
    source_commit: str,
    artifacts: list[dict[str, str | int]],
    candidate_version: str,
    predecessor_version: str = PREDECESSOR_VERSION,
) -> dict[str, object]:
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    return validate_python310_evidence_data(
        evidence,
        source_commit=source_commit,
        artifacts=artifacts,
        candidate_version=candidate_version,
        predecessor_version=predecessor_version,
    )


def validate_upgrade_rollback_evidence_data(
    evidence: object,
    *,
    source_commit: str,
    artifacts: list[dict[str, str | int]],
    predecessor_version: str,
    candidate_version: str,
) -> dict[str, object]:
    if not isinstance(evidence, dict):
        raise ValueError("installed application evidence must be a JSON object")
    _phase, phase_code = phase_for_version(candidate_version)
    baseline = evidence.get("baseline")
    upgrade = evidence.get("upgrade")
    rollback = evidence.get("rollback")
    if (
        evidence.get("schema") != f"hedron.phase-{phase_code}-python311-upgrade-rollback/1"
        or evidence.get("source_commit") != source_commit
        or evidence.get("predecessor_version") != predecessor_version
        or evidence.get("candidate_version") != candidate_version
        or not str(evidence.get("python", "")).startswith("3.11.")
        or evidence.get("platform") in (None, "")
        or evidence.get("architecture") in (None, "")
        or not isinstance(baseline, dict)
        or baseline.get("result") != "pass"
        or baseline.get("hedron") != predecessor_version
        or not isinstance(upgrade, dict)
        or upgrade.get("result") != "pass"
        or upgrade.get("hedron") != candidate_version
        or not isinstance(rollback, dict)
        or rollback.get("result") != "pass"
        or rollback.get("hedron") != predecessor_version
        or rollback.get("restored_original_lock") is not True
        or not isinstance(baseline.get("uv_lock_sha256"), str)
        or not isinstance(upgrade.get("uv_lock_sha256"), str)
        or rollback.get("uv_lock_sha256") != baseline.get("uv_lock_sha256")
    ):
        raise ValueError("installed application upgrade/rollback evidence is incomplete")
    for section, lock_key in (
        (baseline, "uv_lock_sha256"),
        (upgrade, "uv_lock_sha256"),
    ):
        digest = str(section.get(lock_key, ""))
        if len(digest) != 64 or any(char not in "0123456789abcdef" for char in digest):
            raise ValueError("installed application evidence contains an invalid lock digest")
    if baseline["uv_lock_sha256"] == upgrade["uv_lock_sha256"]:
        raise ValueError("upgrade evidence does not show a candidate lock change")

    candidate_rows = evidence.get("candidate_artifacts")
    if not isinstance(candidate_rows, list) or len(candidate_rows) != 2:
        raise ValueError("installed application evidence must bind both candidate wheels")
    candidate_hashes = {
        str(row.get("name")): str(row.get("sha256"))
        for row in candidate_rows
        if isinstance(row, dict) and row.get("name") and row.get("sha256")
    }
    for distribution in ("hedron", "hedron_core"):
        prefix = f"{distribution}-{candidate_version}-"
        name = next((item for item in candidate_hashes if item.startswith(prefix)), None)
        artifact = next((row for row in artifacts if row["name"] == name), None)
        if artifact is None or artifact.get("sha256") != candidate_hashes.get(name):
            raise ValueError(f"installed application evidence is not bound to {distribution}")
    if len(candidate_hashes) != len(candidate_rows):
        raise ValueError(
            "installed application evidence contains duplicate or malformed wheel rows"
        )
    return evidence


def validate_upgrade_rollback_evidence(
    evidence_path: Path,
    *,
    source_commit: str,
    artifacts: list[dict[str, str | int]],
    predecessor_version: str,
    candidate_version: str,
) -> dict[str, object]:
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    return validate_upgrade_rollback_evidence_data(
        evidence,
        source_commit=source_commit,
        artifacts=artifacts,
        predecessor_version=predecessor_version,
        candidate_version=candidate_version,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("first_build", type=Path)
    parser.add_argument("second_build", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--source-commit", required=True)
    parser.add_argument("--retention-reference", required=True)
    parser.add_argument("--python310-evidence", type=Path, required=True)
    parser.add_argument("--upgrade-rollback-evidence", type=Path, required=True)
    parser.add_argument("--predecessor-version")
    args = parser.parse_args(argv)

    if len(args.source_commit) != 40 or any(
        c not in "0123456789abcdef" for c in args.source_commit
    ):
        parser.error("--source-commit must be a full lowercase Git commit hash")
    if not args.retention_reference.strip():
        parser.error("--retention-reference must identify where both builds are retained")
    try:
        packages = expected_packages()
        phase, phase_code = phase_for_version(packages["hedron"])
        expected_predecessor = predecessor_for_version(packages["hedron"])
        if args.predecessor_version is None:
            args.predecessor_version = expected_predecessor
        if args.predecessor_version != expected_predecessor:
            raise ValueError(
                f"phase {phase} requires predecessor {expected_predecessor}, "
                f"got {args.predecessor_version}"
            )
        artifacts = compare_builds(args.first_build, args.second_build, packages=packages)
        python310_evidence = validate_python310_evidence(
            args.python310_evidence,
            source_commit=args.source_commit,
            artifacts=artifacts,
            candidate_version=packages["hedron"],
            predecessor_version=args.predecessor_version,
        )
        upgrade_rollback_evidence = validate_upgrade_rollback_evidence(
            args.upgrade_rollback_evidence,
            source_commit=args.source_commit,
            artifacts=artifacts,
            predecessor_version=args.predecessor_version,
            candidate_version=packages["hedron"],
        )
        uv_version = subprocess.check_output(["uv", "--version"], cwd=ROOT, text=True).strip()
    except (OSError, ValueError, subprocess.CalledProcessError, json.JSONDecodeError) as exc:
        print(str(exc), file=sys.stderr)
        return 1

    payload = {
        "schema": f"hedron.phase-{phase_code}-python-artifact-evidence/1",
        "phase": phase,
        "target": f"v{packages['hedron']}",
        "predecessor_version": args.predecessor_version,
        "source_commit": args.source_commit,
        "command": (
            "SOURCE_DATE_EPOCH=315619200 PYTHONDONTWRITEBYTECODE=1 "
            "uv build --package <each publish-order package except hedron-native>"
        ),
        "environment": {
            "python": ".".join(str(part) for part in sys.version_info[:3]),
            "uv": uv_version,
            "os": platform.platform(),
            "architecture": platform.machine(),
            "source_date_epoch": 315619200,
        },
        "reproducibility": {
            "repeat_builds": 2,
            "comparison": "byte-for-byte SHA-256 equality",
            "verified": True,
        },
        "retention_reference": args.retention_reference,
        "packages": list(packages),
        "artifacts": artifacts,
        "python310_compatibility": python310_evidence,
        "installed_application_upgrade_rollback": upgrade_rollback_evidence,
    }
    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"ok: {len(packages)} distributions / {len(artifacts)} reproducible artifacts")
    print(f"evidence: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

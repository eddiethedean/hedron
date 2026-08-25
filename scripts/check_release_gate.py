#!/usr/bin/env python3
"""Fail if a release tag is not ready for public publication."""

from __future__ import annotations

import argparse
import re
import shlex
import subprocess
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
    "0.13": ROOT / "docs" / "acceptance" / "release-gate-0.13.toml",
    "0.14": ROOT / "docs" / "acceptance" / "release-gate-0.14.toml",
    "0.15": ROOT / "docs" / "acceptance" / "release-gate-0.15.toml",
    "0.16": ROOT / "docs" / "acceptance" / "release-gate-0.16.toml",
    "0.17": ROOT / "docs" / "acceptance" / "release-gate-0.17.toml",
    "0.18": ROOT / "docs" / "acceptance" / "release-gate-0.18.toml",
    "0.19": ROOT / "docs" / "acceptance" / "release-gate-0.19.toml",
    "0.20": ROOT / "docs" / "acceptance" / "release-gate-0.20.toml",
    "0.21": ROOT / "docs" / "acceptance" / "release-gate-0.21.toml",
    "0.22": ROOT / "docs" / "acceptance" / "release-gate-0.22.toml",
    "0.23": ROOT / "docs" / "acceptance" / "release-gate-0.23.toml",
    "0.24": ROOT / "docs" / "acceptance" / "release-gate-0.24.toml",
    "0.25": ROOT / "docs" / "acceptance" / "release-gate-0.25.toml",
    "0.26": ROOT / "docs" / "acceptance" / "release-gate-0.26.toml",
    "0.27": ROOT / "docs" / "acceptance" / "release-gate-0.27.toml",
    "0.28": ROOT / "docs" / "acceptance" / "release-gate-0.28.toml",
    "0.29": ROOT / "docs" / "acceptance" / "release-gate-0.29.toml",
    "0.30": ROOT / "docs" / "acceptance" / "release-gate-0.30.toml",
    "0.31": ROOT / "docs" / "acceptance" / "release-gate-0.31.toml",
    "0.32": ROOT / "docs" / "acceptance" / "release-gate-0.32.toml",
    "0.33": ROOT / "docs" / "acceptance" / "release-gate-0.33.toml",
    "0.34": ROOT / "docs" / "acceptance" / "release-gate-0.34.toml",
    "0.35": ROOT / "docs" / "acceptance" / "release-gate-0.35.toml",
    "0.36": ROOT / "docs" / "acceptance" / "release-gate-0.36.toml",
    "0.37": ROOT / "docs" / "acceptance" / "release-gate-0.37.toml",
    "0.38": ROOT / "docs" / "acceptance" / "release-gate-0.38.toml",
    "0.39": ROOT / "docs" / "acceptance" / "release-gate-0.39.toml",
    "0.40": ROOT / "docs" / "acceptance" / "release-gate-0.40.toml",
    "0.42": ROOT / "docs" / "acceptance" / "release-gate-0.42.toml",
    "0.43": ROOT / "docs" / "acceptance" / "release-gate-0.43.toml",
    "0.44": ROOT / "docs" / "acceptance" / "release-gate-0.44.toml",
    "0.45": ROOT / "docs" / "acceptance" / "release-gate-0.45.toml",
    "0.47": ROOT / "docs" / "acceptance" / "release-gate-0.47.toml",
    "0.48": ROOT / "docs" / "acceptance" / "release-gate-0.48.toml",
    "0.49": ROOT / "docs" / "acceptance" / "release-gate-0.49.toml",
    "0.50": ROOT / "docs" / "acceptance" / "release-gate-0.50.toml",
    "0.51": ROOT / "docs" / "acceptance" / "release-gate-0.51.toml",
    "0.52": ROOT / "docs" / "acceptance" / "release-gate-0.52.toml",
    "0.53": ROOT / "docs" / "acceptance" / "release-gate-0.53.toml",
    "0.54": ROOT / "docs" / "acceptance" / "release-gate-0.54.toml",
    "0.55": ROOT / "docs" / "acceptance" / "release-gate-0.55.toml",
    "0.56": ROOT / "docs" / "acceptance" / "release-gate-0.56.toml",
    "0.57": ROOT / "docs" / "acceptance" / "release-gate-0.57.toml",
    "0.58": ROOT / "docs" / "acceptance" / "release-gate-0.58.toml",
    "0.59": ROOT / "docs" / "acceptance" / "release-gate-0.59.toml",
    "0.60": ROOT / "docs" / "acceptance" / "release-gate-0.60.toml",
    "0.61": ROOT / "docs" / "acceptance" / "release-gate-0.61.toml",
    "0.62": ROOT / "docs" / "acceptance" / "release-gate-0.62.toml",
    "0.63": ROOT / "docs" / "acceptance" / "release-gate-0.63.toml",
    "0.64": ROOT / "docs" / "acceptance" / "release-gate-0.64.toml",
    "0.65": ROOT / "docs" / "acceptance" / "release-gate-0.65.toml",
    "0.66": ROOT / "docs" / "acceptance" / "release-gate-0.66.toml",
}
DEFAULT_EVIDENCE = EVIDENCE_BY_MAJOR_MINOR["0.6"]
# Includes historical ``release`` attestation used by older gate manifests.
KNOWN_CI_JOBS = frozenset(
    {"test", "quality", "browser", "evidence", "realwb", "realconnect", "packaging", "release"}
)
# Commands that must not be re-entered from --execute-verified.
_RECURSIVE_SCRIPT_NAMES = frozenset(
    {
        "check_release_gate.py",
        "verify_pkg_09.py",
        "verify_pkg_10.py",
        "verify_pkg_11.py",
        "verify_pkg_12.py",
        "verify_pkg_13.py",
        "verify_pkg_14.py",
        "verify_pkg_15.py",
        "verify_pkg_16.py",
        "verify_pkg_17.py",
        "verify_pkg_18.py",
        "verify_pkg_19.py",
        "verify_pkg_20.py",
        "verify_pkg_21.py",
        "verify_pkg_22.py",
        "verify_pkg_23.py",
        "verify_pkg_24.py",
        "verify_pkg_25.py",
        "verify_pkg_26.py",
        "verify_pkg_27.py",
        "verify_pkg_28.py",
        "verify_pkg_29.py",
        "verify_pkg_30.py",
        "verify_pkg_31.py",
        "verify_pkg_32.py",
        "verify_pkg_33.py",
        "verify_pkg_34.py",
        "verify_pkg_35.py",
        "verify_pkg_36.py",
        "verify_pkg_37.py",
        "verify_pkg_38.py",
        "verify_pkg_43.py",
        "verify_pkg_44.py",
        "verify_pkg_45.py",
        "verify_pkg_46.py",
        "verify_pkg_47.py",
        "verify_pkg_48.py",
        "verify_pkg_49.py",
        "verify_pkg_50.py",
        "verify_pkg_51.py",
        "verify_pkg_56.py",
        "verify_pkg_57.py",
        "verify_pkg_58.py",
        "verify_pkg_60.py",
        "verify_pkg_61.py",
        "ci_checks.sh",
    }
)


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


def _is_independent_version_package(project: dict[str, object]) -> bool:
    """True when the package versions independently of the Beta flagship train.

    Alpha satellites always version independently. Beta packages on the ``0.1.x``
    satellite line (charts/native after 0.28 graduation) also stay independent of
    the ``0.N.0`` train tag. ``fastapi-workbench`` 1.x versions independently per D-058.
    ``hedron-mcp`` ``0.2.x`` Beta is an independent satellite per D-060 / RFC-0065.
    ``hedron-charts`` ``0.2.x`` Beta is an independent satellite per D-066 / RFC-0069.
    ``hedron-sample-kit`` / ``hedron-notebook`` / ``hedron-sim`` ``0.2.x`` Beta are
    independent satellites per D-093 / RFC-0081.
    """
    if _is_alpha_package(project):
        return True
    name = str(project.get("name", ""))
    if name in {
        "fastapi-workbench",
        "hedron-mcp",
        "hedron-gradio",
        "hedron-charts",
        "hedron-sample-kit",
        "hedron-notebook",
        "hedron-sim",
    }:
        return True
    version = str(project.get("version", ""))
    return version.startswith("0.1.")


def check_packages(tag_version: str) -> list[str]:
    errors: list[str] = []
    if not (ROOT / "LICENSE").is_file():
        errors.append("missing root LICENSE (required before public publication)")

    workspace = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]
    workspace_version = str(workspace["version"])
    if workspace_version != tag_version:
        errors.append(f"hedron-workspace: version {workspace_version!r} != tag {tag_version!r}")

    for pyproject in sorted((ROOT / "packages").glob("*/pyproject.toml")):
        data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
        project = data["project"]
        name = str(project["name"])
        version = str(project["version"])
        independent = _is_independent_version_package(project)
        # Independent satellites (Alpha or 0.1.x Beta) version off the flagship train.
        expected = version if independent else tag_version
        if not independent and version != tag_version:
            errors.append(f"{name}: package version {version!r} != tag {tag_version!r}")
        if "license" not in project and "license-files" not in project:
            errors.append(f"{name}: [project].license (or license-files) is required")
        pkg_dir = pyproject.parent
        module_name = name.replace("-", "_")
        init = pkg_dir / "src" / module_name / "__init__.py"
        if not init.is_file():
            errors.append(f"{name}: primary __init__ missing at {init.relative_to(ROOT)}")
            continue
        init_text = init.read_text(encoding="utf-8")
        match = re.search(r'^__version__\s*=\s*["\']([^"\']+)["\']', init_text, re.M)
        if not match:
            errors.append(f"{name}: __version__ not found in {init}")
        elif match.group(1) != expected:
            errors.append(f"{name}: __version__ {match.group(1)!r} != package {expected!r}")
        for plugin in init.parent.rglob("*.py"):
            plugin_match = re.search(
                r"PLUGIN_META\s*=\s*PluginMeta\(.*?\bversion\s*=\s*[\"']([^\"']+)[\"']",
                plugin.read_text(encoding="utf-8"),
                re.S,
            )
            if plugin_match and plugin_match.group(1) != version:
                errors.append(
                    f"{name}: PluginMeta version {plugin_match.group(1)!r} in "
                    f"{plugin.relative_to(pkg_dir)} != package {version!r}"
                )
        changelog = pkg_dir / "CHANGELOG.md"
        if not changelog.is_file():
            errors.append(f"{name}: missing CHANGELOG.md")
        elif f"[{expected}]" not in changelog.read_text(encoding="utf-8"):
            errors.append(f"{name}: CHANGELOG.md lacks [{expected}] section")
    return errors


def _command_tokens(command: str) -> list[str]:
    try:
        return shlex.split(command)
    except ValueError:
        return command.split()


def _referenced_repo_paths(command: str) -> list[str]:
    """Return scripts/ or tests/ path tokens that should exist on disk."""
    paths: list[str] = []
    for token in _command_tokens(command):
        if token.startswith("scripts/") or token.startswith("tests/"):
            paths.append(token)
    return paths


def _is_suite_command(command: str) -> bool:
    tokens = _command_tokens(command)
    if not tokens:
        return False
    joined = " ".join(tokens)
    if "ci_checks.sh" in joined:
        return True
    if tokens[0] in {"pytest", "bash"}:
        return True
    if len(tokens) >= 2 and tokens[0] == "python" and tokens[1] == "-m" and "pytest" in tokens:
        return True
    return any(t.startswith("verify_pkg_") and t.endswith(".py") for t in tokens)


def _is_executable_ssot_command(command: str) -> bool:
    """True for ``python scripts/check_*.py`` style commands safe to run inline."""
    tokens = _command_tokens(command)
    if len(tokens) < 2 or tokens[0] != "python":
        return False
    script = tokens[1]
    if not script.startswith("scripts/") or not script.endswith(".py"):
        return False
    name = Path(script).name
    if name in _RECURSIVE_SCRIPT_NAMES:
        return False
    return name.startswith("check_")


def _validate_verified_command(eid: str, command: str, ci_job: str) -> list[str]:
    errors: list[str] = []
    if not command:
        errors.append(f"{eid}: Verified entries require a named command")
        return errors
    if not ci_job:
        errors.append(f"{eid}: Verified entries require ci_job (CI attestation)")
    elif ci_job not in KNOWN_CI_JOBS:
        errors.append(f"{eid}: unknown ci_job {ci_job!r} (expected one of {sorted(KNOWN_CI_JOBS)})")

    for rel in _referenced_repo_paths(command):
        target = ROOT / rel
        if not target.exists():
            errors.append(f"{eid}: command references missing path {rel}")

    if _is_suite_command(command):
        checks = (ROOT / "scripts" / "ci_checks.sh").read_text(encoding="utf-8")
        workflow = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
        release_wf = ROOT / ".github" / "workflows" / "release.yml"
        attested = False
        if ci_job:
            if f"cmd_{ci_job}" in checks or f"ci_checks.sh {ci_job}" in workflow:
                attested = True
            if ci_job == "release" and release_wf.is_file():
                attested = True
        if ci_job and not attested:
            errors.append(
                f"{eid}: suite command ci_job={ci_job!r} is not attested in "
                "scripts/ci_checks.sh, .github/workflows/ci.yml, or release.yml"
            )
        # pytest-only suite commands must be owned by the test job.
        tokens = _command_tokens(command)
        if "pytest" in tokens and ci_job and ci_job != "test":
            errors.append(f"{eid}: pytest suite commands require ci_job=test")
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
        ci_job = str(row.get("ci_job", "")).strip()
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
        if state == "Verified":
            errors.extend(_validate_verified_command(eid, command, ci_job))
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


def execute_verified_ssot_commands(path: Path) -> list[str]:
    """Run Verified ``python scripts/check_*.py`` commands from the manifest.

    Suite commands (pytest / ci_checks / verify_pkg) are attested via ``ci_job``
    and path checks — not re-executed here (avoids recursion and hour-long nests).
    """
    errors: list[str] = []
    if not path.is_file():
        return [f"missing evidence manifest: {path}"]
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    rows = data.get("evidence")
    if not isinstance(rows, list):
        return [f"{path}: [[evidence]] entries required"]
    executed = 0
    for row in rows:
        if not isinstance(row, dict):
            continue
        if str(row.get("state", "")).strip() != "Verified":
            continue
        eid = str(row.get("id", "")).strip()
        command = str(row.get("command", "")).strip()
        if not _is_executable_ssot_command(command):
            continue
        tokens = _command_tokens(command)
        # Prefer the active interpreter for portability inside uv/venv.
        argv = [sys.executable, *tokens[1:]]
        print("+", *argv)
        try:
            subprocess.check_call(argv, cwd=ROOT)
        except subprocess.CalledProcessError as exc:
            errors.append(f"{eid}: command failed ({exc.returncode}): {command}")
        else:
            executed += 1
    if executed == 0:
        # Not fatal for older manifests with only suite commands — path/ci_job
        # validation still applies. Warn for visibility.
        print("note: no executable SSOT Verified commands in manifest", file=sys.stderr)
    return errors


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
        command = str(row.get("command", "")).strip()
        ci_job = str(row.get("ci_job", "")).strip()
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
        if state == "Verified":
            errors.extend(_validate_verified_command(eid, command, ci_job))
        if state == "Deferred":
            if not str(row.get("rationale", "")).strip():
                errors.append(f"{eid}: Deferred entries require rationale")
            if not str(row.get("destination", "")).strip():
                errors.append(f"{eid}: Deferred entries require destination")
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
    parser.add_argument(
        "--execute-verified",
        action="store_true",
        help=(
            "Execute Verified python scripts/check_*.py commands from the manifest "
            "(suite/verify_pkg commands are attested via ci_job, not re-run)"
        ),
    )
    args = parser.parse_args()
    # Always verify package metadata matches the requested train version.
    # --allow-planned only relaxes evidence closure (Planned/Implemented rows OK).
    errors = check_packages(args.version)
    if not args.skip_evidence:
        manifest = args.evidence_manifest or evidence_manifest_for(args.version)
        if args.allow_planned:
            errors.extend(check_evidence_manifest_lenient(manifest))
        else:
            errors.extend(check_evidence_manifest(manifest))
        if args.execute_verified and not errors:
            errors.extend(execute_verified_ssot_commands(manifest))
    if not (ROOT / "LICENSE").is_file():
        errors.append("missing root LICENSE (required before public publication)")
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(f"ok: release gate for {args.version}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

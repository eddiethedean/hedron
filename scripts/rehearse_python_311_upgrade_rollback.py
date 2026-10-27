#!/usr/bin/env python3
"""Upgrade and roll back an installed 1.1.3 scaffold on Python 3.11."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import subprocess
import sys
import tempfile
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def scaffold_pin(version: str) -> str:
    major, minor, _patch = (int(part) for part in version.split("."))
    return f">={version},<{major}.{minor + 1}"


def find_wheel(dist_dir: Path, distribution: str, version: str) -> Path:
    normalized = distribution.replace("-", "_")
    matches = sorted(dist_dir.glob(f"{normalized}-{version}-*.whl"))
    if len(matches) != 1:
        raise ValueError(
            f"expected one {distribution}=={version} wheel in {dist_dir}; found {len(matches)}"
        )
    return matches[0].resolve()


def run(command: list[str], *, cwd: Path, env: dict[str, str]) -> None:
    print("+", " ".join(command), flush=True)
    subprocess.run(command, cwd=cwd, env=env, check=True)


def installed_versions(python: Path, *, cwd: Path, env: dict[str, str]) -> dict[str, str]:
    output = subprocess.check_output(
        [
            str(python),
            "-c",
            "import importlib.metadata as m, json, sys; "
            "print(json.dumps({'hedron': m.version('hedron'), "
            "'hedron_core': m.version('hedron-core'), "
            "'python': '.'.join(map(str, sys.version_info[:3]))}))",
        ],
        cwd=cwd,
        env=env,
        text=True,
    )
    return json.loads(output)


def smoke_app(python: Path, *, project: Path, env: dict[str, str]) -> None:
    subprocess.run(
        [str(python), "-c", "import app; assert app.app.routes"],
        cwd=project,
        env=env,
        check=True,
    )


def candidate_project_text(
    source: str,
    *,
    predecessor_version: str,
    candidate_version: str,
    hedron_wheel: Path,
    core_wheel: Path,
) -> str:
    parsed = tomllib.loads(source)
    if parsed.get("tool", {}).get("uv", {}).get("sources"):
        raise ValueError("generated application already defines [tool.uv.sources]")
    old_pin = f'"hedron{scaffold_pin(predecessor_version)}"'
    new_pin = f'"hedron{scaffold_pin(candidate_version)}"'
    if source.count(old_pin) != 1:
        raise ValueError(f"expected one generated Hedron pin {old_pin}")
    updated = source.replace(old_pin, new_pin, 1)
    return (
        updated.rstrip()
        + "\n\n[tool.uv.sources]\n"
        + f"hedron = {{ path = {json.dumps(str(hedron_wheel))} }}\n"
        + f"hedron-core = {{ path = {json.dumps(str(core_wheel))} }}\n"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dist_dir", type=Path)
    parser.add_argument("evidence_output", type=Path)
    parser.add_argument("--predecessor-version", default="1.1.3")
    parser.add_argument("--candidate-version", default="1.2.0")
    args = parser.parse_args(argv)

    dist_dir = args.dist_dir.resolve()
    try:
        candidate_hedron = find_wheel(dist_dir, "hedron", args.candidate_version)
        candidate_core = find_wheel(dist_dir, "hedron-core", args.candidate_version)
        source_commit = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip()
    except (OSError, ValueError, subprocess.CalledProcessError) as exc:
        print(f"installed application rehearsal failed: {exc}", file=sys.stderr)
        return 1

    environment = os.environ.copy()
    try:
        with tempfile.TemporaryDirectory(prefix="hedron-phase-120-upgrade-") as temporary:
            root = Path(temporary)
            run(
                ["uv", "venv", str(root / "bootstrap"), "--python", "3.11"],
                cwd=root,
                env=environment,
            )
            bootstrap_python = (
                root / "bootstrap" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
            )
            run(
                [
                    "uv",
                    "pip",
                    "install",
                    "--python",
                    str(bootstrap_python),
                    f"hedron=={args.predecessor_version}",
                ],
                cwd=root,
                env=environment,
            )
            run(
                [str(bootstrap_python), "-m", "hedron", "new", "upgrade-fixture"],
                cwd=root,
                env=environment,
            )
            project = root / "upgrade-fixture"
            app_venv = project / ".venv"
            run(["uv", "venv", str(app_venv), "--python", "3.11"], cwd=project, env=environment)
            app_python = app_venv / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
            run(["uv", "lock", "--python", str(app_python)], cwd=project, env=environment)
            run(
                ["uv", "sync", "--locked", "--python", str(app_python)],
                cwd=project,
                env=environment,
            )
            original_project = (project / "pyproject.toml").read_text(encoding="utf-8")
            original_lock = (project / "uv.lock").read_bytes()
            before = installed_versions(app_python, cwd=project, env=environment)
            if before["hedron"] != args.predecessor_version or not before["python"].startswith(
                "3.11."
            ):
                raise ValueError(f"unexpected installed baseline: {before}")
            smoke_app(app_python, project=project, env=environment)
            baseline_lock_hash = hashlib.sha256(original_lock).hexdigest()

            (project / "pyproject.toml").write_text(
                candidate_project_text(
                    original_project,
                    predecessor_version=args.predecessor_version,
                    candidate_version=args.candidate_version,
                    hedron_wheel=candidate_hedron,
                    core_wheel=candidate_core,
                ),
                encoding="utf-8",
            )
            run(["uv", "lock", "--python", str(app_python)], cwd=project, env=environment)
            candidate_lock = (project / "uv.lock").read_bytes()
            run(
                ["uv", "sync", "--locked", "--python", str(app_python)],
                cwd=project,
                env=environment,
            )
            upgraded = installed_versions(app_python, cwd=project, env=environment)
            if upgraded["hedron"] != args.candidate_version:
                raise ValueError(f"upgrade installed the wrong Hedron version: {upgraded}")
            smoke_app(app_python, project=project, env=environment)
            candidate_lock_hash = hashlib.sha256(candidate_lock).hexdigest()

            (project / "pyproject.toml").write_text(original_project, encoding="utf-8")
            (project / "uv.lock").write_bytes(original_lock)
            run(
                ["uv", "sync", "--locked", "--python", str(app_python)],
                cwd=project,
                env=environment,
            )
            rolled_back = installed_versions(app_python, cwd=project, env=environment)
            if rolled_back != before:
                raise ValueError(f"rollback did not restore the original runtime: {rolled_back}")
            smoke_app(app_python, project=project, env=environment)
            restored_lock_hash = hashlib.sha256((project / "uv.lock").read_bytes()).hexdigest()
            if restored_lock_hash != baseline_lock_hash:
                raise ValueError("rollback did not restore the original uv.lock")
    except (OSError, subprocess.CalledProcessError, ValueError, json.JSONDecodeError) as exc:
        print(f"installed application rehearsal failed: {exc}", file=sys.stderr)
        return 1

    payload = {
        "schema": "hedron.phase-120-python311-upgrade-rollback/1",
        "source_commit": source_commit,
        "predecessor_version": args.predecessor_version,
        "candidate_version": args.candidate_version,
        "python": before["python"],
        "platform": platform.platform(),
        "architecture": platform.machine(),
        "application": "scaffold generated by the installed 1.1.3 CLI",
        "baseline": {
            "result": "pass",
            "hedron": before["hedron"],
            "uv_lock_sha256": baseline_lock_hash,
        },
        "upgrade": {
            "result": "pass",
            "hedron": upgraded["hedron"],
            "uv_lock_sha256": candidate_lock_hash,
        },
        "rollback": {
            "result": "pass",
            "hedron": rolled_back["hedron"],
            "uv_lock_sha256": restored_lock_hash,
            "restored_original_lock": restored_lock_hash == baseline_lock_hash,
        },
        "candidate_artifacts": [
            {
                "name": candidate_hedron.name,
                "sha256": hashlib.sha256(candidate_hedron.read_bytes()).hexdigest(),
            },
            {
                "name": candidate_core.name,
                "sha256": hashlib.sha256(candidate_core.read_bytes()).hexdigest(),
            },
        ],
    }
    output = args.evidence_output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print("ok: installed 1.1.3 scaffold upgraded to 1.2.0 and rolled back with the original lock")
    print(f"evidence: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

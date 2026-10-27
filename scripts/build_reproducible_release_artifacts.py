#!/usr/bin/env python3
"""Build and compare both 1.2.0 Python artifact sets without publishing."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--retention-reference", required=True)
    args = parser.parse_args(argv)

    output = args.output_dir.resolve()
    if output.exists() and any(output.iterdir()):
        parser.error(f"output directory must be empty: {output}")
    first = output / "build-1"
    second = output / "build-2"
    first.mkdir(parents=True, exist_ok=True)
    second.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env["SOURCE_DATE_EPOCH"] = "315619200"
    env["PYTHONDONTWRITEBYTECODE"] = "1"

    try:
        packages = subprocess.check_output(
            [
                sys.executable,
                "-c",
                (
                    "from scripts.verify_release_reproducibility import expected_packages; "
                    "print('\\n'.join(expected_packages()))"
                ),
            ],
            cwd=ROOT,
            text=True,
            env=env,
        ).splitlines()
        source_commit = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip()
        for build_dir in (first, second):
            for package in packages:
                command = ["uv", "build", "--package", package, "--out-dir", str(build_dir)]
                print("+", " ".join(command), flush=True)
                subprocess.run(command, cwd=ROOT, env=env, check=True)
        compatibility_evidence = output / "python310-compatibility.json"
        subprocess.run(
            [
                sys.executable,
                "scripts/check_python_310_candidate.py",
                str(first),
                str(compatibility_evidence),
            ],
            cwd=ROOT,
            env=env,
            check=True,
        )
        upgrade_rollback_evidence = output / "upgrade-rollback-1.2.json"
        subprocess.run(
            [
                sys.executable,
                "scripts/rehearse_python_311_upgrade_rollback.py",
                str(first),
                str(upgrade_rollback_evidence),
            ],
            cwd=ROOT,
            env=env,
            check=True,
        )
        ledger = output / "python-artifacts.json"
        command = [
            sys.executable,
            "scripts/verify_release_reproducibility.py",
            str(first),
            str(second),
            str(ledger),
            "--source-commit",
            source_commit,
            "--retention-reference",
            args.retention_reference,
            "--python310-evidence",
            str(compatibility_evidence),
            "--upgrade-rollback-evidence",
            str(upgrade_rollback_evidence),
        ]
        subprocess.run(command, cwd=ROOT, env=env, check=True)
    except (OSError, subprocess.CalledProcessError) as exc:
        print(f"release artifact rehearsal failed: {exc}", file=sys.stderr)
        return 1

    print(f"artifacts retained under {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

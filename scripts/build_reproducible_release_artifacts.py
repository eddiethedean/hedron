#!/usr/bin/env python3
"""Build and compare both 1.2/1.3 Python artifact sets without publishing."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.verify_release_reproducibility import (  # noqa: E402
    expected_packages,
    phase_for_version,
    predecessor_for_version,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--retention-reference", required=True)
    parser.add_argument("--candidate-version", default="1.2.0")
    parser.add_argument("--predecessor-version")
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
        package_versions = expected_packages()
        phase, _phase_code = phase_for_version(args.candidate_version)
        if package_versions["hedron"] != args.candidate_version:
            raise ValueError(
                f"candidate metadata is {package_versions['hedron']}, "
                f"expected {args.candidate_version}"
            )
        expected_predecessor = predecessor_for_version(args.candidate_version)
        if args.predecessor_version is None:
            args.predecessor_version = expected_predecessor
        if args.predecessor_version != expected_predecessor:
            raise ValueError(
                f"phase {phase} requires predecessor {expected_predecessor}, "
                f"got {args.predecessor_version}"
            )
        packages = list(package_versions)
        if not args.retention_reference.strip():
            raise ValueError("retention reference must identify where both builds are retained")
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
                "--candidate-version",
                args.candidate_version,
                "--predecessor-version",
                args.predecessor_version,
            ],
            cwd=ROOT,
            env=env,
            check=True,
        )
        upgrade_rollback_evidence = output / f"upgrade-rollback-{phase}.json"
        subprocess.run(
            [
                sys.executable,
                "scripts/rehearse_python_311_upgrade_rollback.py",
                str(first),
                str(upgrade_rollback_evidence),
                "--candidate-version",
                args.candidate_version,
                "--predecessor-version",
                args.predecessor_version,
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
            "--predecessor-version",
            args.predecessor_version,
        ]
        subprocess.run(command, cwd=ROOT, env=env, check=True)
    except (OSError, ValueError, subprocess.CalledProcessError) as exc:
        print(f"release artifact rehearsal failed: {exc}", file=sys.stderr)
        return 1

    print(f"artifacts retained under {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

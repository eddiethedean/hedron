#!/usr/bin/env python3
"""Prove a coordinated 1.2/1.3 wheel rejects Python 3.10 and resolution falls back."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PREDECESSOR_VERSION = "1.1.3"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.verify_release_reproducibility import (  # noqa: E402
    phase_for_version,
    predecessor_for_version,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dist_dir", type=Path)
    parser.add_argument("evidence_output", type=Path)
    parser.add_argument("--predecessor-version")
    parser.add_argument("--candidate-version", default="1.2.0")
    args = parser.parse_args(argv)

    dist_dir = args.dist_dir.resolve()
    try:
        phase, phase_code = phase_for_version(args.candidate_version)
        expected_predecessor = predecessor_for_version(args.candidate_version)
    except ValueError as exc:
        parser.error(str(exc))
    if args.predecessor_version is None:
        args.predecessor_version = expected_predecessor
    if args.predecessor_version != expected_predecessor:
        parser.error(
            f"phase {phase} requires predecessor {expected_predecessor}, "
            f"got {args.predecessor_version}"
        )
    wheels = sorted(dist_dir.glob(f"hedron-{args.candidate_version}-*.whl"))
    if len(wheels) != 1:
        parser.error(
            f"expected one Hedron {args.candidate_version} wheel in {dist_dir}; found {len(wheels)}"
        )
    candidate_wheel = wheels[0]
    environment = os.environ.copy()
    with tempfile.TemporaryDirectory(prefix=f"hedron-phase-{phase_code}-py310-") as temporary:
        venv = Path(temporary) / ".venv"
        try:
            subprocess.run(
                ["uv", "venv", str(venv), "--python", "3.10"],
                check=True,
                env=environment,
            )
            python = venv / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
            rejected = subprocess.run(
                [
                    "uv",
                    "pip",
                    "install",
                    "--no-deps",
                    "--python",
                    str(python),
                    str(candidate_wheel),
                ],
                check=False,
                capture_output=True,
                text=True,
                env=environment,
            )
            rejection_output = rejected.stdout + rejected.stderr
            if rejected.returncode == 0:
                raise ValueError(
                    f"Python 3.10 unexpectedly accepted the {args.candidate_version} Hedron wheel"
                )
            if "3.10" not in rejection_output or "3.11" not in rejection_output:
                raise ValueError(
                    "candidate installation failed without identifying the Python 3.10/3.11 "
                    "Requires-Python boundary"
                )

            subprocess.run(
                ["uv", "pip", "install", "--no-deps", "--python", str(python), "hedron"],
                check=True,
                env=environment,
            )
            resolved = subprocess.check_output(
                [
                    str(python),
                    "-c",
                    "import importlib.metadata as m, json, sys; "
                    "print(json.dumps({'version': m.version('hedron'), "
                    "'python': '.'.join(map(str, sys.version_info[:3]))}))",
                ],
                text=True,
                env=environment,
            )
        except (OSError, subprocess.CalledProcessError, ValueError) as exc:
            print(f"Python 3.10 release compatibility check failed: {exc}", file=sys.stderr)
            return 1

    resolved_facts = json.loads(resolved)
    if resolved_facts.get("version") != args.predecessor_version:
        print(
            "Python 3.10 unpinned resolver expected Hedron "
            f"{args.predecessor_version}, found {resolved_facts.get('version')!r}",
            file=sys.stderr,
        )
        return 1
    if not str(resolved_facts.get("python", "")).startswith("3.10."):
        print("resolver fallback evidence was not produced on Python 3.10", file=sys.stderr)
        return 1

    source_commit = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
    ).strip()
    payload = {
        "schema": f"hedron.phase-{phase_code}-python310-compatibility/1",
        "phase": phase,
        "candidate_version": args.candidate_version,
        "source_commit": source_commit,
        "python": resolved_facts["python"],
        "candidate_install": "rejected by Requires-Python",
        "candidate_artifact": candidate_wheel.name,
        "candidate_sha256": hashlib.sha256(candidate_wheel.read_bytes()).hexdigest(),
        "candidate_rejection_mentions_python_310_and_311": True,
        "unpinned_requirement": "hedron",
        "resolved_version": resolved_facts["version"],
        "predecessor_version": args.predecessor_version,
        "platform": platform.platform(),
        "architecture": platform.machine(),
    }
    output = args.evidence_output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(
        f"ok: {args.candidate_version} candidate rejected on Python 3.10; "
        f"resolver selected {args.predecessor_version}"
    )
    print(f"evidence: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

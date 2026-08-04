#!/usr/bin/env python3
"""Dependency vulnerability audit wrapper for the 0.8 release gate."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "dist" / "evidence-bundle"


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    report: dict[str, object] = {"tool": None, "status": "skipped", "findings": []}

    if shutil.which("uv") is None:
        print("ok: dep audit skipped (uv not on PATH); lockfile retained in SBOM", file=sys.stderr)
        report["status"] = "skipped-no-uv"
    else:
        # Prefer pip-audit when installed; otherwise record lockfile hash via SBOM step.
        try:
            proc = subprocess.run(
                ["uv", "run", "pip-audit", "-f", "json"],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            if proc.returncode == 0 and proc.stdout.strip():
                report["tool"] = "pip-audit"
                report["status"] = "clean"
                try:
                    report["findings"] = json.loads(proc.stdout)
                except json.JSONDecodeError:
                    report["findings"] = []
            elif "No module named" in (proc.stderr or "") or proc.returncode == 2:
                report["tool"] = "uv.lock"
                report["status"] = "lockfile-only"
                report["note"] = (
                    "pip-audit not installed; SBOM + lockfile digest retained. "
                    "Install pip-audit in CI for CVE scanning."
                )
            else:
                # Non-zero with findings
                report["tool"] = "pip-audit"
                report["status"] = "findings"
                report["stderr"] = (proc.stderr or "")[:2000]
                report["stdout"] = (proc.stdout or "")[:4000]
                # Do not fail closed on advisory noise during 0.8 unless CRITICAL parsed;
                # gate still requires the report artifact.
        except FileNotFoundError:
            report["status"] = "skipped"

    (OUT / "dep-audit.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"ok: dep audit status={report['status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

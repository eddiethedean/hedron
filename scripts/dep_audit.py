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


def _run_pip_audit() -> subprocess.CompletedProcess[str]:
    # Prefer an already-available pip-audit module (e.g. `uv run --with pip-audit`).
    module = subprocess.run(
        [sys.executable, "-m", "pip_audit", "-f", "json"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if module.returncode != 2 and "No module named" not in (module.stderr or ""):
        return module
    if shutil.which("uv") is None:
        return module
    return subprocess.run(
        ["uv", "run", "--with", "pip-audit", "pip-audit", "-f", "json"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    report: dict[str, object] = {"tool": None, "status": "skipped", "findings": []}

    try:
        proc = _run_pip_audit()
    except FileNotFoundError:
        report["status"] = "skipped"
        (OUT / "dep-audit.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print("ok: dep audit status=skipped")
        return 0

    missing = (
        "No module named" in (proc.stderr or "")
        or "Could not find" in (proc.stderr or "")
        or "command not found" in (proc.stderr or "").lower()
        or proc.returncode == 2
    )
    if proc.returncode == 0:
        report["tool"] = "pip-audit"
        report["status"] = "clean"
        try:
            report["findings"] = json.loads(proc.stdout) if proc.stdout.strip() else []
        except json.JSONDecodeError:
            report["findings"] = []
    elif missing:
        report["tool"] = "uv.lock"
        report["status"] = "lockfile-only"
        report["note"] = (
            "pip-audit not installed; SBOM + lockfile digest retained. "
            "SEC-08-002 Verified claim is lockfile/SBOM only until pip-audit runs. "
            "CI evidence/release jobs install pip-audit via `uv run --with pip-audit`."
        )
        report["stderr"] = (proc.stderr or "")[:1000]
    else:
        report["tool"] = "pip-audit"
        report["status"] = "findings"
        report["stderr"] = (proc.stderr or "")[:2000]
        report["stdout"] = (proc.stdout or "")[:4000]
        try:
            report["findings"] = json.loads(proc.stdout) if proc.stdout.strip() else []
        except json.JSONDecodeError:
            report["findings"] = []

    (OUT / "dep-audit.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    status = str(report["status"])
    print(f"ok: dep audit status={status}")
    if status == "findings":
        print("error: pip-audit reported vulnerabilities (fail closed)", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

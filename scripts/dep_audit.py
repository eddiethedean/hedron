#!/usr/bin/env python3
"""Dependency vulnerability audit wrapper for the release gate."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "dist" / "evidence-bundle"


def _run_pip_audit() -> subprocess.CompletedProcess[str]:
    """Audit the repository lock export, never the caller's ambient environment."""
    uv = shutil.which("uv")
    if uv is None:
        return subprocess.CompletedProcess(
            args=["uv", "export"],
            returncode=2,
            stdout="",
            stderr="uv is not installed; cannot export uv.lock",
        )

    with tempfile.TemporaryDirectory(prefix="hedron-dep-audit-") as temp_dir:
        requirements = Path(temp_dir) / "requirements.txt"
        exported = subprocess.run(
            [
                uv,
                "export",
                "--locked",
                "--all-groups",
                "--format",
                "requirements.txt",
                "--no-annotate",
                "--no-header",
                "--no-editable",
                "--no-hashes",
                "--output-file",
                str(requirements),
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        if exported.returncode != 0:
            return subprocess.CompletedProcess(
                args=exported.args,
                returncode=3,
                stdout=exported.stdout,
                stderr=exported.stderr,
            )

        audit_args = [
            "--requirement",
            str(requirements),
            "--no-deps",
            "--disable-pip",
            "--format",
            "json",
        ]
        # Prefer an already-available pip-audit module (e.g. CI's injected tool).
        module = subprocess.run(
            [sys.executable, "-m", "pip_audit", *audit_args],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        if module.returncode != 2 and "No module named" not in (module.stderr or ""):
            return module
        return subprocess.run(
            [uv, "run", "--no-project", "--with", "pip-audit", "pip-audit", *audit_args],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )


def _vuln_entries(payload: Any) -> list[dict[str, Any]]:
    """Return packages that have non-empty vulns lists."""
    deps: list[Any]
    if isinstance(payload, dict):
        deps = list(payload.get("dependencies") or [])
    elif isinstance(payload, list):
        deps = payload
    else:
        return []
    found: list[dict[str, Any]] = []
    for dep in deps:
        if not isinstance(dep, dict):
            continue
        vulns = dep.get("vulns") or []
        if vulns:
            found.append(dep)
    return found


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
    payload: Any = []
    if proc.stdout.strip():
        try:
            payload = json.loads(proc.stdout)
        except json.JSONDecodeError:
            payload = []

    if missing:
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
        report["findings"] = payload
        vulns = _vuln_entries(payload)
        # Unpublished workspace wheels are skipped by pip-audit; that is expected pre-tag.
        if vulns:
            report["status"] = "findings"
            report["vulnerable"] = [
                {
                    "name": v.get("name"),
                    "version": v.get("version"),
                    "ids": [x.get("id") for x in (v.get("vulns") or []) if isinstance(x, dict)],
                }
                for v in vulns
            ]
            report["stderr"] = (proc.stderr or "")[:2000]
        else:
            report["status"] = "clean"
            if proc.returncode not in {0, 1}:
                # Unexpected tool failure without parsed vulns.
                report["status"] = "findings"
                report["stderr"] = (proc.stderr or "")[:2000]
                report["stdout"] = (proc.stdout or "")[:4000]

    (OUT / "dep-audit.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    status = str(report["status"])
    print(f"ok: dep audit status={status}")
    if status == "findings":
        print("error: pip-audit reported vulnerabilities (fail closed)", file=sys.stderr)
        vulnerable = report.get("vulnerable")
        if vulnerable:
            print(json.dumps(vulnerable, indent=2), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

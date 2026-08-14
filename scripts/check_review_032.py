#!/usr/bin/env python3
"""REVIEW-032: redacted security review packet + disposition + adversarial suite."""

from __future__ import annotations

import subprocess
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "docs" / "acceptance" / "security-review-032"
REPORT = PACKET / "REDACTED_REPORT.md"
BRIEF = PACKET / "BRIEF.md"
DISPOSITION = PACKET / "DISPOSITION.toml"
ADVERSARIAL = ROOT / "tests" / "security" / "test_mcp_adversarial.py"


def main() -> int:
    errors: list[str] = []
    for path in (REPORT, BRIEF, DISPOSITION, ADVERSARIAL):
        if not path.is_file():
            errors.append(f"missing {path.relative_to(ROOT)}")

    if REPORT.is_file():
        text = REPORT.read_text(encoding="utf-8")
        for needle in (
            "REVIEW-032",
            "critical",
            "high",
            "deny-by-default",
            "confused",
            "exfiltration",
        ):
            if needle.lower() not in text.lower():
                errors.append(f"REDACTED_REPORT.md missing {needle!r}")

    if DISPOSITION.is_file():
        data = tomllib.loads(DISPOSITION.read_text(encoding="utf-8"))
        findings = data.get("findings")
        if not isinstance(findings, list):
            errors.append("DISPOSITION.toml requires [[findings]]")
        else:
            open_critical = [
                f
                for f in findings
                if isinstance(f, dict)
                and str(f.get("severity", "")).lower() in {"critical", "high"}
                and str(f.get("status", "")).lower() not in {"fixed", "accepted_risk", "mitigated"}
            ]
            if open_critical:
                errors.append(f"open critical/high findings: {open_critical}")
        if data.get("critical_high_open") is not False:
            errors.append("DISPOSITION.toml critical_high_open must be false at Verified")

    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1

    cmd = [
        sys.executable,
        "-m",
        "pytest",
        str(ADVERSARIAL.relative_to(ROOT)),
        "-q",
        "--tb=short",
    ]
    print("+", *cmd)
    try:
        subprocess.check_call(cmd, cwd=ROOT)
    except subprocess.CalledProcessError as exc:
        print(f"REVIEW-032 adversarial suite failed ({exc.returncode})", file=sys.stderr)
        return 1
    print("ok: REVIEW-032 security review packet")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

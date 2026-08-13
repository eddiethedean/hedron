#!/usr/bin/env python3
"""DOCS-033: Posit docs packet + strict MkDocs build."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from _gate_033 import fail_errors, require_files  # noqa: E402


def main() -> int:
    errors: list[str] = []
    require_files(
        [
            ROOT / "docs" / "acceptance" / "RELEASE_0_33.md",
            ROOT / "docs" / "rfcs" / "RFC-0066-HEDRON-POSIT.md",
            ROOT / "docs" / "guides" / "posit.md",
            ROOT / "docs" / "guides" / "posit-workbench.md",
            ROOT / "docs" / "guides" / "whats-new-0.33.md",
            ROOT / "docs" / "packages" / "hedron-posit.md",
            ROOT / "docs" / "implementation" / "HEDRON_POSIT_033.md",
        ],
        errors,
    )
    guide = (ROOT / "docs" / "guides" / "posit.md").read_text(encoding="utf-8")
    for needle in (
        "HedronPosit",
        "ConnectCookieMode",
        "authenticated_header_v1",
        "2025.05.1",
        "2025.06.0",
        "2026.07.0",
        "BRIDGE_DECISION",
    ):
        if needle not in guide:
            errors.append(f"docs/guides/posit.md missing {needle!r}")
    if fail_errors(errors, "DOCS-033"):
        return 1
    cmd = [
        "uv",
        "run",
        "--group",
        "docs",
        "mkdocs",
        "build",
        "--strict",
        "-f",
        str(ROOT / "mkdocs.yml"),
    ]
    print("+", *cmd)
    try:
        subprocess.check_call(cmd, cwd=ROOT)
    except subprocess.CalledProcessError as exc:
        print(f"DOCS-033 mkdocs failed ({exc.returncode})", file=sys.stderr)
        return 1
    print("ok: DOCS-033")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

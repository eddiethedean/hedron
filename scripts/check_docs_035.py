#!/usr/bin/env python3
"""DOCS-035: fleet docs packet + strict MkDocs + inventory honesty needles."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from _gate_035 import (  # noqa: E402
    IMPLEMENTATION,
    INVENTORY,
    RELEASE_PACKET,
    RFC,
    fail_errors,
    require_files,
)


def main() -> int:
    errors: list[str] = []
    require_files(
        [
            RELEASE_PACKET,
            RFC,
            IMPLEMENTATION,
            INVENTORY,
            ROOT / "docs" / "guides" / "whats-ready.md",
            ROOT / "docs" / "guides" / "whats-new-0.35.md",
            ROOT / "docs" / "COMPATIBILITY.md",
        ],
        errors,
    )
    whats = (ROOT / "docs" / "guides" / "whats-ready.md").read_text(encoding="utf-8")
    release = RELEASE_PACKET.read_text(encoding="utf-8") if RELEASE_PACKET.is_file() else ""
    inv = INVENTORY.read_text(encoding="utf-8") if INVENTORY.is_file() else ""
    combined = whats + release + inv
    for needle in (
        "production_grade",
        "PRESENT-034",
        "deferred_to_fleet_docs_audit",
        "hedron-gradio",
        "0.35",
    ):
        if needle not in combined:
            errors.append(f"docs missing fleet marker {needle!r}")
    if "Alpha satellite" in whats and "hedron[gradio]" in whats:
        errors.append("whats-ready still labels Gradio as Alpha satellite")
    if fail_errors(errors, "DOCS-035"):
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
        print(f"DOCS-035 mkdocs failed ({exc.returncode})", file=sys.stderr)
        return 1
    print("ok: DOCS-035")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

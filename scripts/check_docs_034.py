#!/usr/bin/env python3
"""DOCS-034: Gradio docs packet + strict MkDocs build."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from _gate_034 import IMPLEMENTATION, RELEASE_PACKET, RFC, fail_errors, require_files  # noqa: E402


def main() -> int:
    errors: list[str] = []
    require_files(
        [
            RELEASE_PACKET,
            RFC,
            IMPLEMENTATION,
            ROOT / "docs" / "guides" / "gradio-migration.md",
            ROOT / "docs" / "guides" / "whats-new-0.34.md",
            ROOT / "docs" / "packages" / "hedron-gradio.md",
            ROOT / "packages" / "hedron-gradio" / "README.md",
        ],
        errors,
    )
    guide = (ROOT / "docs" / "guides" / "gradio-migration.md").read_text(encoding="utf-8")
    pkg = (ROOT / "docs" / "packages" / "hedron-gradio.md").read_text(encoding="utf-8")
    combined = guide + pkg
    for needle in ("allowlist", "GradioRemoteConfig", "0.2.0"):
        if needle not in combined:
            errors.append(f"docs missing Gradio 0.34 marker {needle!r}")
    if fail_errors(errors, "DOCS-034"):
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
        print(f"DOCS-034 mkdocs failed ({exc.returncode})", file=sys.stderr)
        return 1
    print("ok: DOCS-034")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""REALWB-029: Docker Workbench smoke evidence.

Default: validate a redacted RESULT.log (no Docker on every CI run).
Live: ``--live`` or ``HEDRON_REALWB=1`` runs ``scripts/realwb_029.sh``.
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "docs" / "acceptance" / "realwb-029" / "RESULT.log"
SCRIPT = ROOT / "scripts" / "realwb_029.sh"
REQUIRED_MARKERS = (
    "REALWB-029",
    "image=",
    "rserver-url=",
    "RSERVER_URL=",
    "PROXY_E2E=",
    "LAUNCHER_PATH=",
    "PAGE=",
    "FRAGMENT=",
    "CSRF=",
    "ASSETS=",
    "OPENAPI=",
    "REDIRECT=",
    "ENCODED_TARGET=",
    "TARGET_GUARDS=",
    "DIAGNOSTICS=",
    "EXTERNAL_URL=",
    "WEBSOCKET=",
    "OUTSIDE_WORKBENCH=",
    "RESULT=pass",
)
FORBIDDEN = (
    "WORKBENCH_API_KEY=",
    "PWB_LICENSE=",
    "6IX8-",
)
SECRET_PATTERNS = (
    re.compile(r"\b[A-Za-z0-9]{4}(?:-[A-Za-z0-9]{4}){5,}\b"),
    re.compile(r"(?i)\b(?:api[_ -]?key|token|secret)\s*[=:]\s*[^*\s,]+"),
)


def _validate_log(text: str) -> list[str]:
    errors: list[str] = []
    for marker in REQUIRED_MARKERS:
        if marker not in text:
            errors.append(f"RESULT.log missing {marker!r}")
    for needle in FORBIDDEN:
        if needle in text:
            errors.append(f"RESULT.log leaked secret-like token {needle!r}")
    for pattern in SECRET_PATTERNS:
        if pattern.search(text):
            errors.append("RESULT.log contained a product-license or secret-shaped value")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--live",
        action="store_true",
        help="Run Docker smoke (also HEDRON_REALWB=1).",
    )
    args = parser.parse_args(argv)
    live = args.live or os.environ.get("HEDRON_REALWB", "").strip() in {"1", "true", "yes"}
    RESULT.parent.mkdir(parents=True, exist_ok=True)

    if live:
        if not SCRIPT.is_file():
            print(f"missing {SCRIPT}", file=sys.stderr)
            return 1
        print("+", "bash", SCRIPT)
        try:
            subprocess.check_call(["bash", str(SCRIPT)], cwd=ROOT)
        except subprocess.CalledProcessError as exc:
            print(f"realwb_029.sh failed ({exc.returncode})", file=sys.stderr)
            return 1

    if not RESULT.is_file():
        print(
            f"missing {RESULT.relative_to(ROOT)} — run with --live / HEDRON_REALWB=1",
            file=sys.stderr,
        )
        return 1
    text = RESULT.read_text(encoding="utf-8")
    errors = _validate_log(text)
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print("ok: REALWB-029")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

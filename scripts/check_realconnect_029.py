#!/usr/bin/env python3
"""Validate or run the licensed Posit Connect Docker evidence."""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "docs" / "acceptance" / "realconnect-029" / "RESULT.log"
SCRIPT = ROOT / "scripts" / "realconnect_029.sh"
REQUIRED_MARKERS = (
    "REALCONNECT-029",
    "image=",
    "CONNECT_HEALTH=",
    "CONNECT_BOOTSTRAP=",
    "CONNECT_DEPLOY=",
    "PAGE=",
    "FRAGMENT=",
    "CSRF=",
    "ASSETS=",
    "OPENAPI=",
    "REDIRECT=",
    "DIAGNOSTICS=",
    "EXTERNAL_URL=",
    "WORKBENCH_ISOLATION=",
    "WEBSOCKET=",
    "OUTSIDE_CONNECT=",
    "RESULT=pass",
)
FORBIDDEN = (
    "CONNECT_API_KEY=",
    "PCT_LICENSE=",
    "CONNECT_BOOTSTRAP_SECRETKEY=",
)
SECRET_PATTERNS = (
    re.compile(r"\b[A-Za-z0-9]{4}(?:-[A-Za-z0-9]{4}){5,}\b"),
    re.compile(r"(?i)\b(?:api[_ -]?key|token|secret)\s*[=:]\s*[^*\s,]+"),
)


def _validate_log(text: str) -> list[str]:
    errors = [f"RESULT.log missing {marker!r}" for marker in REQUIRED_MARKERS if marker not in text]
    errors.extend(
        f"RESULT.log leaked secret environment name {needle!r}"
        for needle in FORBIDDEN
        if needle in text
    )
    errors.extend(
        "RESULT.log contained a product-license or secret-shaped value"
        for pattern in SECRET_PATTERNS
        if pattern.search(text)
    )
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true", help="Run the Docker smoke first.")
    args = parser.parse_args(argv)
    live = args.live or os.environ.get("HEDRON_REALCONNECT", "").strip().lower() in {
        "1",
        "true",
        "yes",
    }
    if live:
        try:
            subprocess.check_call(["bash", str(SCRIPT)], cwd=ROOT)
        except subprocess.CalledProcessError as exc:
            print(f"realconnect_029.sh failed ({exc.returncode})", file=sys.stderr)
            return 1
    if not RESULT.is_file():
        print(f"missing {RESULT.relative_to(ROOT)} — run with --live", file=sys.stderr)
        return 1
    errors = _validate_log(RESULT.read_text(encoding="utf-8"))
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print("ok: REALCONNECT-029")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

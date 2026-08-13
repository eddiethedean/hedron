#!/usr/bin/env python3
"""REALCONNECT-033: Docker Connect smoke evidence for hedron-posit cookie features.

Default: validate a redacted RESULT.log (no Docker on every CI run).
Live: ``--live`` or ``HEDRON_REALCONNECT=1`` runs ``scripts/realconnect_033_probe.sh``.
When the live smoke cannot use ``CONNECT_LICENSE`` (expired or activation limit), it
exits 42 and this checker reports a successful skip instead of failing CI.
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "docs" / "acceptance" / "realconnect-033" / "RESULT.log"
SCRIPT = ROOT / "scripts" / "realconnect_033_probe.sh"
SHARED_MARKERS = (
    "REALCONNECT-033",
    "image=",
    "CONNECT_HEALTH=",
    "CONNECT_BOOTSTRAP=",
    "CONNECT_DEPLOY=",
    "RESULT=pass",
)
COOKIE_MARKERS = (
    "PAGE=ok",
    "cookie_path=runtime_repaired",
    "FRAGMENT=ok",
    "CSRF=ok",
    "NATIVE_COOKIES=ok",
    "BRIDGE_DECISION=",
)
MATRIX_MARKERS = (
    "FIXTURES=ok",
    "ASSETS=ok",
    "OPENAPI=ok",
    "REDIRECT=ok",
    "DIAGNOSTICS=ok",
    "EXTERNAL_URL=ok",
    "WORKBENCH_ISOLATION=ok",
    "WEBSOCKET=ok",
    "OUTSIDE_CONNECT=ok",
)
REQUIRED_MARKERS = SHARED_MARKERS + COOKIE_MARKERS + MATRIX_MARKERS
FORBIDDEN = (
    "CONNECT_LICENSE=",
    "CONNECT_API_KEY=",
    "PCT_LICENSE=",
    "CONNECT_BOOTSTRAP_SECRETKEY=",
)
SECRET_PATTERNS = (
    re.compile(r"\b[A-Za-z0-9]{4}(?:-[A-Za-z0-9]{4}){5,}\b"),
    re.compile(r"(?i)\b(?:api[_ -]?key|token|secret)\s*[=:]\s*[^*\s,]+"),
)
SKIP_EXIT_CODE = 42


def _validate_log(text: str) -> list[str]:
    errors: list[str] = []
    for marker in REQUIRED_MARKERS:
        if marker not in text:
            errors.append(f"RESULT.log missing {marker!r}")
    for needle in FORBIDDEN:
        if needle in text:
            errors.append(f"RESULT.log leaked secret environment name {needle!r}")
    for pattern in SECRET_PATTERNS:
        if pattern.search(text):
            errors.append("RESULT.log contained a product-license or secret-shaped value")
    if "NATIVE_COOKIES=fail" in text:
        errors.append("RESULT.log recorded NATIVE_COOKIES=fail (native cookie round-trip broken)")
    if "BRIDGE_DECISION=keep_supported" in text:
        errors.append(
            "RESULT.log recorded BRIDGE_DECISION=keep_supported "
            "(Supported native cookie lane would be blocked)"
        )
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--live",
        action="store_true",
        help="Run Docker smoke (also HEDRON_REALCONNECT=1).",
    )
    args = parser.parse_args(argv)
    live = args.live or os.environ.get("HEDRON_REALCONNECT", "").strip() in {"1", "true", "yes"}
    RESULT.parent.mkdir(parents=True, exist_ok=True)

    if live:
        if not SCRIPT.is_file():
            print(f"missing {SCRIPT}", file=sys.stderr)
            return 1
        py = ROOT / ".venv" / "bin" / "python"
        if not py.is_file():
            print(
                "missing .venv — run: uv sync --frozen --all-extras --python 3.12",
                file=sys.stderr,
            )
            return 1
        print("+", "bash", SCRIPT)
        try:
            subprocess.check_call(["bash", str(SCRIPT)], cwd=ROOT)
        except subprocess.CalledProcessError as exc:
            if exc.returncode == SKIP_EXIT_CODE:
                print("skip: REALCONNECT-033 (CONNECT_LICENSE unavailable)")
                return 0
            print(f"realconnect_033_probe.sh failed ({exc.returncode})", file=sys.stderr)
            return 1

    if not RESULT.is_file():
        print(
            f"missing {RESULT.relative_to(ROOT)} — run with --live / HEDRON_REALCONNECT=1",
            file=sys.stderr,
        )
        return 1
    text = RESULT.read_text(encoding="utf-8")
    errors = _validate_log(text)
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print("ok: REALCONNECT-033 (hedron-posit Connect native cookies)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""REALWB-030: Docker Workbench smoke evidence for hedron-workbench, hedron-posit, and fastapi-workbench.

Default: validate redacted RESULT.log files (no Docker on every CI run).
Live: ``--live`` or ``HEDRON_REALWB=1`` runs ``scripts/realwb_smoke.sh`` (current 2026.07.0 lane).
The 2025.05.1 floor log is committed evidence from ``scripts/realwb_202505_probe.sh``.
When the live smoke cannot use ``PWB_LICENSE`` (expired or activation limit), it
exits 42 and this checker reports a successful skip instead of failing CI.
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "docs" / "acceptance" / "realwb-030" / "RESULT.log"
RESULT_FLOOR = ROOT / "docs" / "acceptance" / "realwb-030-202505" / "RESULT.log"
SCRIPT = ROOT / "scripts" / "realwb_smoke.sh"
FLOOR_SCRIPT = ROOT / "scripts" / "realwb_202505_probe.sh"
PROBE_DOC = ROOT / "docs" / "acceptance" / "WORKBENCH_PROBE_030.md"
WORKBENCH_GUIDE = ROOT / "docs" / "guides" / "posit-workbench.md"
SHARED_MARKERS = (
    "REALWB-030",
    "image=",
    "rserver-url=",
    "RSERVER_URL=",
    "PROXY_E2E=",
    "RESULT=pass",
)
HEDRON_MARKERS = (
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
    "HEDRON_PACKAGE=pass",
)
POSIT_MARKERS = (
    "POSIT_LAUNCHER_PATH=",
    "POSIT_PAGE=",
    "POSIT_REDIRECT=",
    "POSIT_DIAGNOSTICS=",
    "POSIT_OUTSIDE_WORKBENCH=",
    "POSIT_PACKAGE=pass",
)
FASTAPI_MARKERS = (
    "FASTAPI_LAUNCHER_PATH=",
    "FASTAPI_PAGE=",
    "FASTAPI_POST=",
    "FASTAPI_OPENAPI=",
    "FASTAPI_REDIRECT=",
    "FASTAPI_ENCODED_TARGET=",
    "FASTAPI_TARGET_GUARDS=",
    "FASTAPI_DIAGNOSTICS=",
    "FASTAPI_WEBSOCKET=",
    "FASTAPI_OUTSIDE_WORKBENCH=",
    "FASTAPI_PACKAGE=pass",
)
REQUIRED_MARKERS = SHARED_MARKERS + HEDRON_MARKERS + FASTAPI_MARKERS
FLOOR_MARKERS = (
    "REALWB-030-202505",
    "2025.05.1",
    "docker_platform=linux/amd64",
    "HEDRON_PACKAGE=pass",
    "POSIT_PACKAGE=pass",
    "FASTAPI_PACKAGE=pass",
    "RESULT=pass",
)
FORBIDDEN = (
    "PWB_LICENSE=",
    "6IX8-",
)
SECRET_PATTERNS = (
    re.compile(r"\b[A-Za-z0-9]{4}(?:-[A-Za-z0-9]{4}){5,}\b"),
    re.compile(r"(?i)\b(?:api[_ -]?key|token|secret)\s*[=:]\s*[^*\s,]+"),
)
SKIP_EXIT_CODE = 42
MAX_AGE = timedelta(days=45)


def _secret_errors(text: str, label: str) -> list[str]:
    errors: list[str] = []
    for needle in FORBIDDEN:
        if needle in text:
            errors.append(f"{label} leaked secret-like token {needle!r}")
    for pattern in SECRET_PATTERNS:
        if pattern.search(text):
            errors.append(f"{label} contained a product-license or secret-shaped value")
    return errors


def _validate_log(text: str) -> list[str]:
    errors: list[str] = []
    for marker in REQUIRED_MARKERS:
        if marker not in text:
            errors.append(f"RESULT.log missing {marker!r}")
    errors.extend(_secret_errors(text, "RESULT.log"))
    return errors


def _validate_floor_log(text: str) -> list[str]:
    errors: list[str] = []
    for marker in FLOOR_MARKERS + HEDRON_MARKERS + POSIT_MARKERS + FASTAPI_MARKERS:
        if marker not in text:
            errors.append(f"realwb-030-202505 RESULT.log missing {marker!r}")
    if "rstudio-server=" in text and "2025.05.1" not in text:
        errors.append("realwb-030-202505 RESULT.log missing Workbench 2025.05.1 pin")
    errors.extend(_secret_errors(text, "realwb-030-202505 RESULT.log"))
    match = re.search(r"REALWB-030-202505 start (\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z)", text)
    if not match:
        errors.append("realwb-030-202505 RESULT.log missing start timestamp")
        return errors
    started = datetime.strptime(match.group(1), "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    age = datetime.now(timezone.utc) - started
    if age > MAX_AGE:
        errors.append(
            f"realwb-030-202505 RESULT.log is stale ({age.days} days); refresh live smoke"
        )
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--live",
        action="store_true",
        help="Run Docker smoke for the current 2026.07.0 lane (also HEDRON_REALWB=1).",
    )
    args = parser.parse_args(argv)
    live = args.live or os.environ.get("HEDRON_REALWB", "").strip() in {"1", "true", "yes"}
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
                print("skip: REALWB-030 (PWB_LICENSE unavailable)")
                return 0
            print(f"realwb_smoke.sh failed ({exc.returncode})", file=sys.stderr)
            return 1

    errors: list[str] = []
    if not RESULT.is_file():
        errors.append(f"missing {RESULT.relative_to(ROOT)} — run with --live / HEDRON_REALWB=1")
    else:
        errors.extend(_validate_log(RESULT.read_text(encoding="utf-8")))

    if not FLOOR_SCRIPT.is_file():
        errors.append(f"missing {FLOOR_SCRIPT.relative_to(ROOT)}")
    if not PROBE_DOC.is_file():
        errors.append(f"missing {PROBE_DOC.relative_to(ROOT)}")
    if not WORKBENCH_GUIDE.is_file():
        errors.append(f"missing {WORKBENCH_GUIDE.relative_to(ROOT)}")
    else:
        guide = WORKBENCH_GUIDE.read_text(encoding="utf-8")
        for needle in ("2025.05.1", "2026.07.0"):
            if needle not in guide:
                errors.append(f"docs/guides/posit-workbench.md missing {needle!r}")
    if not RESULT_FLOOR.is_file():
        errors.append(
            f"missing {RESULT_FLOOR.relative_to(ROOT)} — run bash scripts/realwb_202505_probe.sh"
        )
    else:
        errors.extend(_validate_floor_log(RESULT_FLOOR.read_text(encoding="utf-8")))

    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print("ok: REALWB-030 (hedron-workbench + hedron-posit + fastapi-workbench)")
    print("ok: REALWB-030-202505 (Workbench 2025.05.1 floor)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

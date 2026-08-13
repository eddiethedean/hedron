#!/usr/bin/env python3
"""CONNECT-033: licensed native Connect matrix + unit fixtures."""

from __future__ import annotations

import re
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from _gate_033 import (  # noqa: E402
    FIXTURES,
    PROBE_RESULT,
    fail_errors,
    require_dirs,
    require_files,
    require_inventory_keys,
    run_pytest,
)


def _result_freshness_errors(text: str, errors: list[str]) -> None:
    if "RESULT=pass" not in text:
        errors.append("realconnect-033 RESULT.log missing RESULT=pass")
    if "NATIVE_COOKIES=ok" not in text:
        errors.append("realconnect-033 RESULT.log missing NATIVE_COOKIES=ok")
    if "CONNECT_VERSION=2026.07.0" not in text and "version=2026.07.0" not in text:
        # Accept either field name used by probe variants.
        if "2026.07.0" not in text:
            errors.append("realconnect-033 RESULT.log missing Connect 2026.07.0 pin")
    match = re.search(r"REALCONNECT-033 start (\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z)", text)
    if not match:
        errors.append("realconnect-033 RESULT.log missing start timestamp")
        return
    started = datetime.strptime(match.group(1), "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=UTC)
    age = datetime.now(UTC) - started
    if age > timedelta(days=45):
        errors.append(
            f"realconnect-033 RESULT.log is stale ({age.days} days); refresh live smoke"
        )


def main() -> int:
    errors: list[str] = []
    require_files(
        [
            PROBE_RESULT,
            ROOT / "docs" / "acceptance" / "CONNECT_PROBE_033.md",
            ROOT / "examples" / "connect-reference" / "app.py",
            ROOT / "packages" / "hedron-posit" / "src" / "hedron_posit" / "connect.py",
            ROOT / "packages" / "hedron-posit" / "src" / "hedron_posit" / "products.py",
        ],
        errors,
    )
    require_dirs([FIXTURES], errors)
    require_inventory_keys(
        "hedron-posit",
        supported=("native_connect", "posit_config", "connect_config"),
        experimental=("off_host_connect", "vanity_url_matrix_expansion"),
        errors=errors,
    )
    example = (ROOT / "examples" / "connect-reference" / "app.py").read_text(encoding="utf-8")
    if "HedronPosit" not in example:
        errors.append("connect-reference must deploy HedronPosit")
    if PROBE_RESULT.is_file():
        _result_freshness_errors(PROBE_RESULT.read_text(encoding="utf-8"), errors)
    if fail_errors(errors, "CONNECT-033"):
        return 1
    return run_pytest(
        [
            "tests/adapters/posit/test_resolve_connect.py",
            "tests/adapters/posit/test_compat.py",
        ],
        "CONNECT-033",
    )


if __name__ == "__main__":
    raise SystemExit(main())

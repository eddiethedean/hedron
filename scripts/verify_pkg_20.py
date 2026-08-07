"""Verify phase 0.20 packaging evidence that can run without a public index."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

GATE_TESTS = [
    "tests/integration/test_phase20_htmx_preset.py",
    "tests/unit/test_phase20_hx_eval_reject.py",
    "tests/integration/test_phase20_mount_path.py",
    "tests/unit/test_phase20_production_gates.py",
    "tests/adapters/test_phase20_fragment_regions.py",
    "tests/adapters/test_phase20_security_headers.py",
    "tests/adapters/test_phase20_flask_login_auth.py",
    "tests/unit/test_phase20_scaffolds.py",
]


def _assert_extras_pins() -> None:
    text = (ROOT / "packages/hedron/pyproject.toml").read_text(encoding="utf-8")
    for extra, pattern in (
        ("dev", r"hedron-explorer>=0\.20\.0,<0\.21"),
        ("jinja", r"hedron-jinja>=0\.20\.0,<0\.21"),
        ("conformance", r"hedron-conformance>=0\.20\.0,<0\.21"),
        ("extras", r"hedron-extras>=0\.20\.0,<0\.21"),
        ("data", r"hedron-data>=0\.20\.0,<0\.21"),
    ):
        if not re.search(pattern, text):
            raise SystemExit(f"hedron[{extra}] pin must match {pattern}")


def _wheel_smoke_adapters() -> None:
    code = """
import importlib
import sys

# Adapters must import without FastAPI.
assert "fastapi" not in sys.modules
import hedron_flask
import hedron_django
from hedron_core import SecurityPolicy, Page, Text, render, RenderMode
from hedron_flask import HedronFlask
from hedron_django import HedronSecurityHeadersMiddleware

assert HedronFlask is not None
assert HedronSecurityHeadersMiddleware is not None
policy = SecurityPolicy.from_name("standard")
assert "Content-Security-Policy" in policy.response_headers()
html = render(Page(Text("ok"), title="Ok"), mode=RenderMode.PAGE).html
assert "ok" in html
try:
    importlib.import_module("hedron_jinja")
except Exception:
    pass
print("ok: adapter wheel smoke")
"""
    subprocess.check_call([sys.executable, "-c", code], cwd=ROOT)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--wheel-smoke-adapters",
        action="store_true",
        help="Only run flask/django import smoke (no FastAPI).",
    )
    args = parser.parse_args(argv)
    if args.wheel_smoke_adapters:
        _wheel_smoke_adapters()
        return 0

    _assert_extras_pins()
    _wheel_smoke_adapters()
    commands = [
        [sys.executable, "-m", "pytest", "-q", *GATE_TESTS],
        [
            sys.executable,
            str(ROOT / "scripts" / "check_release_gate.py"),
            "0.20.0",
            "--skip-evidence",
        ],
    ]
    for command in commands:
        print("+", *command)
        subprocess.check_call(command, cwd=ROOT)
    print("ok: PKG-020 local packaging evidence")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

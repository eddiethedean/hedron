#!/usr/bin/env python3
"""Executable release gates for phase 0.66 HDJ parity."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNTIME_GATES = {
    "BINDING-066",
    "REGISTRY-066",
    "INTERACTION-066",
    "CONTEXT-066",
    "PROVIDER-066",
    "STYLE-066",
}
GATES = {
    "CONTRACT-066",
    *RUNTIME_GATES,
    "SECURITY-066",
    "COMPAT-066",
    "DOCS-066",
    "PKG-066",
    "REGRESS-066",
}


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def _text(path: str) -> str:
    candidate = ROOT / path
    _require(candidate.is_file(), f"missing phase 0.66 artifact: {path}")
    return candidate.read_text(encoding="utf-8")


def _pytest(*paths: str) -> None:
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", *paths, "--tb=short", "-n", "0"],
        cwd=ROOT,
        check=False,
    )
    if result.returncode:
        raise SystemExit(result.returncode)


def _contract() -> None:
    for path in (
        "docs/rfcs/RFC-0093-HDJ-PARITY-AND-REGISTRY-INTEGRATION.md",
        "docs/implementation/HDJ_PARITY_066.md",
        "docs/acceptance/RELEASE_0_66.md",
        "docs/acceptance/release-gate-0.66.toml",
        "docs/acceptance/hdj-parity-capability-inventory-066.toml",
        "docs/acceptance/open-issues-066.toml",
    ):
        text = _text(path)
        _require("0.66" in text, f"phase identity missing from {path}")
    inventory = _text("docs/acceptance/hdj-parity-capability-inventory-066.toml")
    _require('id = "DYNAMIC-NAMESPACE-066"' in inventory, "dynamic namespace deferral missing")
    _require('state = "Deferred"' in inventory, "deferred state missing")
    issues = _text("docs/acceptance/open-issues-066.toml")
    for number in range(718, 731):
        _require(
            f"number = {number}" in issues,
            f"open issue #{number} missing from 0.66 inventory",
        )
    _require('status = "Verified"' in issues, "0.66 issue inventory is not Verified")
    _require("open_issue_count = 0" in issues, "0.66 open issue count is not zero")
    _require("closed_as_implemented = [613, 140]" in issues, "implemented issue audit is missing")
    for number in range(718, 731):
        _require(
            f"number = {number}" in issues and 'state = "Verified"' in issues,
            f"issue gate #{number} is not Verified",
        )


def _docs() -> None:
    api = _text("docs/api/HDJ_PARITY_066.md")
    for symbol in ("JinjaBinding", "h_view", "h_command_form", "h_type_schema", "hdj.htmx"):
        _require(symbol in api, f"0.66 API docs omit {symbol}")


def _package() -> None:
    package = _text("packages/hedron-jinja/pyproject.toml")
    facade = _text("packages/hedron-jinja/src/hedron_jinja/__init__.py")
    workspace = _text("pyproject.toml")
    release = _text("docs/release.toml")
    _require('version = "0.66.0"' in package, "hedron-jinja package version is not 0.66.0")
    _require(
        '"hedron-core>=0.66.0,<0.67"' in package,
        "hedron-jinja core dependency is not on the 0.66 train",
    )
    _require('__version__ = "0.66.0"' in facade, "hedron-jinja facade version is not 0.66.0")
    _require('version = "0.66.0"' in workspace, "workspace version is not 0.66.0")
    _require(
        'development_version = "0.66.0"' in release,
        "release metadata development version is not 0.66.0",
    )
    for symbol in ("JinjaBinding", "ApplicationStyleFact", "maps_provider_manifest"):
        _require(f'"{symbol}"' in facade, f"public facade omits {symbol}")
    with tempfile.TemporaryDirectory() as directory:
        result = subprocess.run(
            [
                "uv",
                "build",
                "--package",
                "hedron-jinja",
                "--wheel",
                "--out-dir",
                directory,
            ],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
            env={
                **os.environ,
                "UV_CACHE_DIR": os.environ.get("UV_CACHE_DIR", "/tmp/hedron-uv-cache"),
            },
        )
        _require(result.returncode == 0, result.stdout[-1000:] + result.stderr[-1000:])
        wheels = sorted(Path(directory).glob("*.whl"))
        _require(bool(wheels), "hedron-jinja wheel was not produced")
        with zipfile.ZipFile(wheels[0]) as wheel:
            names = set(wheel.namelist())
        _require(
            "hedron_jinja/binding.py" in names,
            "hedron-jinja wheel omits the 0.66 binding module",
        )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gate", choices=sorted(GATES), required=True)
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    _require(args.verify, "phase 0.66 gates require --verify")

    if args.gate == "CONTRACT-066":
        _contract()
    elif args.gate in RUNTIME_GATES:
        _pytest("tests/jinja/test_hdj_0_66.py")
    elif args.gate == "SECURITY-066":
        _pytest(
            "tests/jinja/test_hdj_0_66.py",
            "tests/jinja/test_evidence_09_002.py",
            "tests/jinja/test_hdj_0_11.py",
        )
    elif args.gate == "COMPAT-066":
        _pytest("tests/jinja/test_integration.py", "tests/unit/test_authoring_045.py")
    elif args.gate == "DOCS-066":
        _docs()
    elif args.gate == "PKG-066":
        _package()
    elif args.gate == "REGRESS-066":
        _pytest("tests/jinja", "tests/unit/test_phase066_issue_gates.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

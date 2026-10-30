#!/usr/bin/env python3
"""Run an isolated browser failure with synthetic secrets and scan its manifest."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
import uuid
from pathlib import Path
from xml.etree import ElementTree

ROOT = Path(__file__).resolve().parents[1]
PROBE_TEST = "tests/browser/test_ui_testing_privacy_canary.py"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--browser", choices=("chromium", "firefox", "webkit"), required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    args = parser.parse_args(argv)

    secret = f"hedron_privacy_{uuid.uuid4().hex}"
    temp_parent = Path(os.environ.get("TMPDIR", tempfile.gettempdir())).resolve()
    errors: list[str] = []
    with tempfile.TemporaryDirectory(prefix="hedron-privacy-", dir=temp_parent) as temp_name:
        temp_root = Path(temp_name)
        artifact_root = temp_root / f"artifacts-{secret}-path"
        output_root = temp_root / "browser-output"
        junit_path = temp_root / "canary.xml"
        environment = os.environ.copy()
        environment.update(
            {
                "HEDRON_BROWSER": "1",
                "HEDRON_BROWSER_ENGINE": args.browser,
                "HEDRON_UI_CANARY_PROBE": "1",
                "HEDRON_UI_CANARY_SECRET": secret,
            }
        )
        command = [
            sys.executable,
            "-m",
            "pytest",
            "-q",
            "-n",
            "0",
            "--browser",
            args.browser,
            "--tracing",
            "off",
            "--screenshot",
            "off",
            "--video",
            "off",
            "--output",
            str(output_root),
            "--hedron-ui-artifacts",
            str(artifact_root),
            f"--junitxml={junit_path}",
            PROBE_TEST,
        ]
        try:
            completed = subprocess.run(
                command,
                cwd=ROOT,
                env=environment,
                capture_output=True,
                text=True,
                timeout=180,
                check=False,
            )
        except subprocess.TimeoutExpired:
            errors.append("privacy canary pytest process exceeded 180 seconds")
            completed = None

        manifest_paths = (
            sorted(artifact_root.rglob("manifest.json")) if artifact_root.exists() else []
        )
        manifest_bytes = b""
        manifest: dict[str, object] = {}
        if len(manifest_paths) != 1:
            errors.append(f"expected one structured manifest, found {len(manifest_paths)}")
        else:
            manifest_bytes = manifest_paths[0].read_bytes()
            try:
                parsed = json.loads(manifest_bytes)
                if isinstance(parsed, dict):
                    manifest = parsed
                else:
                    errors.append("structured manifest root was not an object")
            except json.JSONDecodeError:
                errors.append("structured manifest was not valid JSON")

        canary_suffixes = (
            "_form",
            "_query",
            "_header",
            "_cookie",
            "_storage",
            "_console",
            "_exception",
            "_target",
            "_path",
        )
        leaked = [
            suffix.removeprefix("_")
            for suffix in canary_suffixes
            if f"{secret}{suffix}".encode() in manifest_bytes
        ]
        failure_type = "unavailable"
        expected_exception_seen = False
        failure_message_length = 0
        failure_contains_runtime_error = False
        failure_contains_assertion_error = False
        failure_exception_names: list[str] = []
        if leaked:
            errors.append("structured manifest retained one or more confidential canary values")
        if completed is not None:
            if completed.returncode != 1:
                errors.append("privacy canary pytest did not report its intentional failure")
            try:
                junit_root = ElementTree.parse(junit_path).getroot()
            except (OSError, ElementTree.ParseError):
                errors.append("privacy canary pytest did not produce readable JUnit evidence")
            else:
                cases = list(junit_root.iter("testcase"))
                if len(cases) != 1 or cases[0].find("failure") is None:
                    errors.append("privacy canary did not reach its intentional failure assertion")
                else:
                    failure = cases[0].find("failure")
                    failure_text = ""
                    if failure is not None:
                        failure_type = failure.get("type", "unavailable")
                        failure_text = failure.get("message", "") + (failure.text or "")
                        failure_message_length = len(failure_text)
                        failure_contains_runtime_error = "RuntimeError" in failure_text
                        failure_contains_assertion_error = "AssertionError" in failure_text
                        failure_exception_names = sorted(
                            set(re.findall(r"\b[A-Za-z_]+Error\b", failure_text))
                        )
                    expected_exception_seen = f"{secret}_exception" in failure_text
                    if not expected_exception_seen:
                        errors.append("privacy canary exception value was not exercised")
        if "test_failure" not in manifest.get("failure_categories", []):
            errors.append("structured manifest did not record the failed test category")
        native_output_files = (
            [path for path in output_root.rglob("*") if path.is_file()]
            if output_root.exists()
            else []
        )
        if native_output_files:
            errors.append("structured-only privacy probe unexpectedly wrote native browser output")

        report = {
            "schema_version": 1,
            "lane": "structured-privacy-canary",
            "operating_system": sys.platform,
            "browser": args.browser,
            "status": "passed" if not errors else "failed",
            "canary_categories": [suffix.removeprefix("_") for suffix in canary_suffixes],
            "manifest_count": len(manifest_paths),
            "manifest_bytes": len(manifest_bytes),
            "manifest_leaked_categories": leaked,
            "failure_type": failure_type,
            "failure_message_length": failure_message_length,
            "failure_contains_runtime_error": failure_contains_runtime_error,
            "failure_contains_assertion_error": failure_contains_assertion_error,
            "failure_exception_names": failure_exception_names,
            "expected_exception_seen": expected_exception_seen,
            "intentional_failure_recorded": "test_failure"
            in manifest.get("failure_categories", []),
            "unexpected_native_output_count": len(native_output_files),
            "errors": errors,
        }

    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, sort_keys=True))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())

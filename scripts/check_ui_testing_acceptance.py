#!/usr/bin/env python3
"""Validate Linux UI-testing matrix rows, required browser cases, and skip dispositions."""

from __future__ import annotations

import argparse
import json
import platform
import re
import sys
import tomllib
from collections import Counter
from pathlib import Path
from typing import cast
from xml.etree import ElementTree

ROOT = Path(__file__).resolve().parents[1]
INVENTORY = ROOT / "docs/acceptance/ui-testing-inventory-130.toml"
SKIP_POLICY = ROOT / "docs/acceptance/ui-testing-skip-policy-130.toml"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lane", choices=("host", "browser"), required=True)
    parser.add_argument("--junitxml", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--python", required=True, help="Expected CPython major.minor")
    parser.add_argument("--browser", choices=("chromium", "firefox", "webkit"))
    args = parser.parse_args(argv)

    errors: list[str] = []
    inventory = tomllib.loads(INVENTORY.read_text(encoding="utf-8"))
    skip_policy = tomllib.loads(SKIP_POLICY.read_text(encoding="utf-8"))
    runtime_python = f"{sys.version_info.major}.{sys.version_info.minor}"
    operating_system = platform.system()
    if operating_system != inventory.get("required_os"):
        errors.append(
            f"required OS is {inventory.get('required_os')}; this run is {operating_system}"
        )
    if runtime_python != args.python:
        errors.append(f"expected Python {args.python}; this run is Python {runtime_python}")

    if args.lane == "host":
        if args.python not in inventory.get("host_python_versions", []):
            errors.append(f"Python {args.python} is outside the required host matrix")
        cases = cast(list[dict[str, object]], inventory.get("host_case", []))
        expected_inventory_count = int(
            cast(dict[str, object], inventory.get("coverage", {})).get("required_host_cases", 0)
        )
    else:
        if args.browser is None:
            errors.append("--browser is required for the browser lane")
        if args.python != inventory.get("browser_python_version"):
            errors.append(
                f"browser evidence requires Python {inventory.get('browser_python_version')}"
            )
        if args.browser not in inventory.get("browsers", []):
            errors.append(f"browser {args.browser!r} is outside the required browser matrix")
        cases = cast(list[dict[str, object]], inventory.get("browser_case", []))
        coverage = cast(dict[str, object], inventory.get("coverage", {}))
        expected_inventory_count = int(coverage.get("required_browser_cases", 0))
        gate_counts = Counter(str(case.get("gate", "")) for case in cases)
        for gate, coverage_key in (
            ("BEHAVIOR-130", "behavior_cases"),
            ("A11Y-130", "accessibility_cases"),
        ):
            expected_gate_count = int(coverage.get(coverage_key, 0))
            if gate_counts[gate] != expected_gate_count:
                errors.append(
                    f"{gate} inventory declares {expected_gate_count} cases but contains "
                    f"{gate_counts[gate]}"
                )
        supporting_count = len(cases) - gate_counts["BEHAVIOR-130"] - gate_counts["A11Y-130"]
        expected_supporting_count = int(coverage.get("supporting_browser_cases", 0))
        if supporting_count != expected_supporting_count:
            errors.append(
                f"supporting browser inventory declares {expected_supporting_count} cases but "
                f"contains {supporting_count}"
            )

    if len(cases) != expected_inventory_count:
        errors.append(
            f"acceptance inventory declares {expected_inventory_count} required {args.lane} "
            f"cases but contains {len(cases)}"
        )

    try:
        root = ElementTree.parse(args.junitxml).getroot()
    except (OSError, ElementTree.ParseError) as exc:
        parser.error(f"cannot read JUnit XML {args.junitxml}: {exc}")
    testcases = list(root.iter("testcase"))
    if not testcases:
        errors.append("JUnit report contains no test cases")

    required_results: list[dict[str, object]] = []
    for case in cases:
        matches = _matching_cases(testcases, case, args.browser)
        expected_count = int(case.get("instances", 1))
        result = {
            "id": case.get("id"),
            "test": f"{case.get('file')}::{case.get('name')}",
            "status": "missing",
            "matched_testcases": [],
        }
        if len(matches) != expected_count:
            errors.append(
                f"{case.get('id')}: expected {expected_count} matching test case(s) for "
                f"{case.get('file')}::{case.get('name')} on {args.browser or args.python}; "
                f"found {len(matches)}"
            )
        if matches:
            matched_results: list[dict[str, object]] = []
            statuses: list[str] = []
            for testcase in matches:
                status, reason = _testcase_status(testcase)
                statuses.append(status)
                matched_results.append(
                    {
                        "classname": testcase.get("classname", ""),
                        "name": testcase.get("name", ""),
                        "status": status,
                        "reason": reason,
                        "time_seconds": testcase.get("time", "0"),
                        "properties": _testcase_properties(testcase),
                    }
                )
                if status != "passed":
                    errors.append(
                        f"{case.get('id')}: required testcase {testcase.get('classname')}::"
                        f"{testcase.get('name')} is {status}: {reason or 'no reason supplied'}"
                    )
            result["status"] = "passed" if all(s == "passed" for s in statuses) else "failed"
            result["matched_testcases"] = matched_results
        required_results.append(result)

    classifications = cast(list[dict[str, object]], skip_policy.get("classification", []))
    skip_results: list[dict[str, object]] = []
    if args.lane == "browser":
        for testcase in testcases:
            status, reason = _testcase_status(testcase)
            if status != "skipped":
                continue
            matching_rule = next(
                (
                    rule
                    for rule in classifications
                    if re.search(str(rule.get("reason_regex", "(?!)")), reason or "")
                ),
                None,
            )
            classification = str(matching_rule.get("id")) if matching_rule else None
            allowed = bool(matching_rule and matching_rule.get("allowed_in_browser_lane") is True)
            skip_results.append(
                {
                    "test": f"{testcase.get('classname', '')}::{testcase.get('name', '')}",
                    "reason": reason,
                    "classification": classification,
                    "allowed": allowed,
                }
            )
            if not matching_rule:
                errors.append(
                    f"unclassified skip: {testcase.get('classname')}::{testcase.get('name')}: "
                    f"{reason}"
                )
            elif not allowed:
                errors.append(
                    f"skip disposition {classification} is not allowed in the browser lane: "
                    f"{testcase.get('classname')}::{testcase.get('name')}: {reason}"
                )

    report = {
        "schema_version": 1,
        "phase": "1.3",
        "lane": args.lane,
        "operating_system": operating_system,
        "architecture": platform.machine(),
        "python": runtime_python,
        "browser": args.browser,
        "junitxml": str(args.junitxml),
        "testcase_count": len(testcases),
        "status_counts": dict(Counter(_testcase_status(item)[0] for item in testcases)),
        "required_cases": required_results,
        "skips": skip_results,
        "errors": errors,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    if errors:
        for error in errors:
            print(f"error: {error}", file=sys.stderr)
        print(f"wrote diagnostic report to {args.output}", file=sys.stderr)
        return 1
    print(
        f"ok: {args.lane} acceptance on Linux Python {runtime_python}"
        + (f" / {args.browser}" if args.browser else "")
        + f"; {len(required_results)} required cases passed; "
        + f"{len(skip_results)} skips explicitly classified"
    )
    print(f"report: {args.output}")
    return 0


def _matching_cases(
    testcases: list[ElementTree.Element],
    case: dict[str, object],
    browser: str | None,
) -> list[ElementTree.Element]:
    expected_module = Path(str(case.get("file", ""))).stem
    expected_name = str(case.get("name", ""))
    matches: list[ElementTree.Element] = []
    for testcase in testcases:
        classname = testcase.get("classname", "")
        actual_module = classname.replace(".", "/").rsplit("/", 1)[-1]
        actual_name = testcase.get("name", "")
        actual_base = actual_name.split("[", 1)[0]
        if actual_module != expected_module or actual_base != expected_name:
            continue
        if browser is not None and "[" in actual_name:
            parameters = actual_name.split("[", 1)[1].rsplit("]", 1)[0]
            if browser not in parameters.split("-") and browser not in parameters.split(","):
                continue
        matches.append(testcase)
    return matches


def _testcase_status(testcase: ElementTree.Element) -> tuple[str, str | None]:
    skipped = testcase.find("skipped")
    if skipped is not None:
        return "skipped", skipped.get("message") or skipped.get("type") or "skipped"
    failure = testcase.find("failure")
    if failure is not None:
        return "failed", failure.get("message") or failure.text or "failure"
    error = testcase.find("error")
    if error is not None:
        return "error", error.get("message") or error.text or "error"
    return "passed", None


def _testcase_properties(testcase: ElementTree.Element) -> dict[str, str]:
    allowed = re.compile(
        r"^(?:axe_[a-z0-9_]+|browser_version|context_(?:create|close)_ms|"
        r"event_(?:count|snapshot_bytes)|host_(?:startup|shutdown)_ms|"
        r"host_child_processes|playwright_version|pytest_playwright_version|"
        r"scenario_cycle_ms|settle_ms|structured_manifest_bytes)$"
    )
    return {
        name: value
        for property_node in testcase.findall("./properties/property")
        if (name := property_node.get("name", "")) and allowed.fullmatch(name)
        if (value := property_node.get("value", "")) is not None
    }


if __name__ == "__main__":
    raise SystemExit(main())

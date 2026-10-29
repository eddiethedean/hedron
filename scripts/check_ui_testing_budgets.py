#!/usr/bin/env python3
"""Check measured Linux UI-testing samples against the frozen 1.3 resource budgets."""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
import tomllib
from collections.abc import Mapping
from pathlib import Path
from typing import cast
from xml.etree import ElementTree

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "docs/acceptance/ui-testing-contract-130.toml"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lane", choices=("host", "browser"), required=True)
    parser.add_argument("--python", required=True)
    parser.add_argument("--browser", choices=("chromium", "firefox", "webkit"))
    parser.add_argument("--junitxml", type=Path, required=True)
    parser.add_argument("--resource-report", type=Path, required=True)
    parser.add_argument("--capture-probe", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)

    contract = tomllib.loads(CONTRACT.read_text(encoding="utf-8"))
    budgets = {
        str(row["id"]): cast(Mapping[str, object], row)
        for row in cast(list[dict[str, object]], contract.get("budgets", []))
    }
    errors: list[str] = []
    _validate_frozen_contract(contract, budgets, errors)
    if platform.system() != "Linux":
        errors.append(f"required OS is Linux; this run is {platform.system()}")
    runtime_python = f"{sys.version_info.major}.{sys.version_info.minor}"
    if runtime_python != args.python:
        errors.append(f"expected Python {args.python}; this run is Python {runtime_python}")

    try:
        root = ElementTree.parse(args.junitxml).getroot()
    except (OSError, ElementTree.ParseError) as exc:
        parser.error(f"cannot read JUnit XML {args.junitxml}: {exc}")
    testcases = list(root.iter("testcase"))
    report: dict[str, object] = {
        "schema_version": 1,
        "phase": "1.3",
        "lane": args.lane,
        "operating_system": platform.system(),
        "architecture": platform.machine(),
        "python": runtime_python,
        "browser": args.browser,
        "measurements": {},
        "errors": errors,
    }
    measurements = cast(dict[str, object], report["measurements"])

    if args.lane == "host":
        _check_host(testcases, budgets, measurements, errors)
    else:
        if args.browser is None:
            errors.append("--browser is required for browser budget evidence")
        _check_browser(testcases, budgets, measurements, errors, args.browser)
        if args.capture_probe is None:
            errors.append("browser lane requires --capture-probe evidence")
        else:
            _check_capture(args.capture_probe, budgets, measurements, errors)

    try:
        resource_report = json.loads(args.resource_report.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"cannot read measured resource report: {exc}")
    else:
        _check_parallel(resource_report, budgets, measurements, errors, args.lane)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if errors:
        for error in errors:
            print(f"error: {error}", file=sys.stderr)
        print(f"wrote diagnostic budget report to {args.output}", file=sys.stderr)
        return 1
    print(
        f"ok: frozen {args.lane} resource budgets on Linux Python {runtime_python}"
        + (f" / {args.browser}" if args.browser else "")
    )
    print(f"report: {args.output}")
    return 0


def _check_host(
    testcases: list[ElementTree.Element],
    budgets: Mapping[str, Mapping[str, object]],
    output: dict[str, object],
    errors: list[str],
) -> None:
    host_budget = budgets.get("host", {})
    limit = float(host_budget.get("limit", 0))
    details = cast(Mapping[str, object], host_budget.get("frozen_limits", {}))
    testcase = _find_case(testcases, "test_ui_testing_host", "test_managed_host_resource_budget")
    if testcase is None:
        errors.append("host resource sample test is missing from JUnit")
        return
    properties = _properties(testcase)
    startup = _number_list(properties.get("host_startup_ms"), "host_startup_ms", errors)
    shutdown = _number_list(properties.get("host_shutdown_ms"), "host_shutdown_ms", errors)
    child_processes = _number_list(
        properties.get("host_child_processes"), "host_child_processes", errors
    )
    _require_samples(
        startup, int(details.get("startup_samples_per_row", 0)), "host startup", errors
    )
    _require_samples(
        shutdown, int(details.get("shutdown_samples_per_row", 0)), "host shutdown", errors
    )
    if startup and max(startup) > limit:
        errors.append(f"host startup {max(startup):.2f}ms exceeds frozen {limit:.0f}ms limit")
    shutdown_limit = float(details.get("shutdown_max_ms", 0))
    if shutdown and max(shutdown) > shutdown_limit:
        errors.append(
            f"host shutdown {max(shutdown):.2f}ms exceeds frozen {shutdown_limit:.0f}ms limit"
        )
    if child_processes and max(child_processes) > float(details.get("child_processes_max", 0)):
        errors.append("managed scenario exceeded its frozen child-process count")

    artifact_case = _find_case(
        testcases,
        "test_ui_testing_artifacts",
        "test_artifact_writer_respects_manifest_byte_ceiling",
    )
    artifact_budget = budgets.get("structured_artifacts", {})
    artifact_details = cast(Mapping[str, object], artifact_budget.get("frozen_limits", {}))
    artifact_limit = float(artifact_details.get("max_manifest_bytes", 0))
    if artifact_case is None:
        errors.append("structured artifact size sample is missing from JUnit")
    else:
        manifest_bytes = _number(
            _properties(artifact_case).get("structured_manifest_bytes"),
            "structured_manifest_bytes",
            errors,
        )
        if manifest_bytes is not None and manifest_bytes > artifact_limit:
            errors.append(
                f"structured manifest {manifest_bytes:.0f} bytes exceeds frozen "
                f"{artifact_limit:.0f} bytes limit"
            )
        output["structured_manifest_bytes"] = manifest_bytes
    output["host_startup_ms"] = startup
    output["host_shutdown_ms"] = shutdown
    output["host_child_processes"] = child_processes


def _validate_frozen_contract(
    contract: Mapping[str, object],
    budgets: Mapping[str, Mapping[str, object]],
    errors: list[str],
) -> None:
    if contract.get("numeric_budgets_frozen") is not True:
        errors.append("1.3 contract has not frozen numeric resource budgets")
    for budget_id, budget in budgets.items():
        if budget.get("state") not in {"Frozen", "Measured"}:
            errors.append(f"budget {budget_id} is not frozen")
        if budget.get("threshold_frozen") is not True:
            errors.append(f"budget {budget_id} has no frozen threshold")
        try:
            limit = float(budget.get("limit", 0))
        except (TypeError, ValueError):
            limit = 0
        if limit <= 0 or not str(budget.get("unit", "")).strip():
            errors.append(f"budget {budget_id} needs a positive numeric limit and unit")
        sample_count = budget.get("sample_count")
        if type(sample_count) is not int or sample_count < 0:
            errors.append(f"budget {budget_id} has an invalid sample count")
        elif budget.get("state") == "Measured" and sample_count == 0:
            errors.append(f"measured budget {budget_id} has no measured samples")
        evidence_value = budget.get("measurement_evidence")
        digest_value = budget.get("measurement_sha256")
        if not isinstance(evidence_value, str) or not isinstance(digest_value, str):
            errors.append(f"budget {budget_id} requires hashed measurement evidence")
            continue
        evidence_path = (ROOT / "docs/acceptance" / evidence_value).resolve()
        if not evidence_path.is_relative_to(ROOT) or not evidence_path.is_file():
            errors.append(
                f"budget {budget_id} measurement evidence is missing or escapes the repository"
            )
            continue
        actual_digest = hashlib.sha256(evidence_path.read_bytes()).hexdigest()
        if digest_value != actual_digest:
            errors.append(f"budget {budget_id} measurement evidence SHA-256 does not match")


def _check_browser(
    testcases: list[ElementTree.Element],
    budgets: Mapping[str, Mapping[str, object]],
    output: dict[str, object],
    errors: list[str],
    browser: str | None,
) -> None:
    browser_budget = budgets.get("browser", {})
    browser_limit = float(browser_budget.get("limit", 0))
    browser_details = cast(Mapping[str, object], browser_budget.get("frozen_limits", {}))
    testcase = _find_case(
        testcases,
        "test_ui_testing_resource_budget",
        "test_ui_testing_resource_budget",
    )
    if testcase is None:
        errors.append("browser context/settle resource sample is missing from JUnit")
        return
    properties = _properties(testcase)
    create = _number_list(properties.get("context_create_ms"), "context_create_ms", errors)
    close = _number_list(properties.get("context_close_ms"), "context_close_ms", errors)
    _require_samples(
        create, int(browser_details.get("context_samples_per_row", 0)), "context create", errors
    )
    _require_samples(
        close, int(browser_details.get("context_samples_per_row", 0)), "context close", errors
    )
    for label, values in (("context creation", create), ("context close", close)):
        if values and max(values) > browser_limit:
            errors.append(f"{label} {max(values):.2f}ms exceeds frozen {browser_limit:.0f}ms limit")
    scenario_ms = _number(properties.get("scenario_cycle_ms"), "scenario_cycle_ms", errors)
    scenario_limit = float(browser_details.get("scenario_cycle_max_ms", 0))
    if scenario_ms is not None and scenario_ms > scenario_limit:
        errors.append(
            f"managed scenario {scenario_ms:.2f}ms exceeds frozen {scenario_limit:.0f}ms limit"
        )

    settle_budget = budgets.get("settle", {})
    settle_limit = float(settle_budget.get("limit", 0))
    settle_ms = _number_list(properties.get("settle_ms"), "settle_ms", errors)
    _require_samples(
        settle_ms,
        int(
            cast(Mapping[str, object], settle_budget.get("frozen_limits", {})).get(
                "samples_per_row", 0
            )
        ),
        "settle",
        errors,
    )
    if settle_ms and max(settle_ms) > settle_limit:
        errors.append(f"settle {max(settle_ms):.2f}ms exceeds frozen {settle_limit:.0f}ms limit")
    event_count = _number(properties.get("event_count"), "event_count", errors)
    event_bytes = _number(properties.get("event_snapshot_bytes"), "event_snapshot_bytes", errors)
    if event_count is not None and event_count > float(
        cast(Mapping[str, object], settle_budget.get("frozen_limits", {})).get("event_count_max", 0)
    ):
        errors.append("observed event count exceeds the frozen per-scenario event capacity")
    if event_bytes is not None and event_bytes > float(
        cast(Mapping[str, object], settle_budget.get("frozen_limits", {})).get(
            "event_snapshot_bytes_max", 0
        )
    ):
        errors.append("serialized event snapshot exceeds the frozen byte limit")

    environment = cast(Mapping[str, object], contract_environment())
    for property_name, contract_name in (
        ("playwright_version", "playwright"),
        ("pytest_playwright_version", "pytest_playwright"),
    ):
        expected = str(environment.get(contract_name, ""))
        if properties.get(property_name) != expected:
            errors.append(
                f"{property_name}={properties.get(property_name)!r} does not match frozen "
                f"environment version {expected!r}"
            )
    expected_browser_version = str(environment.get(browser or "", ""))
    if (
        not expected_browser_version
        or properties.get("browser_version") != expected_browser_version
    ):
        errors.append(
            f"browser_version={properties.get('browser_version')!r} does not match frozen "
            f"{browser or 'engine'} version {expected_browser_version!r}"
        )
    output.update(
        {
            "context_create_ms": create,
            "context_close_ms": close,
            "scenario_cycle_ms": scenario_ms,
            "settle_ms": settle_ms,
            "event_count": event_count,
            "event_snapshot_bytes": event_bytes,
            "playwright_version": properties.get("playwright_version"),
            "pytest_playwright_version": properties.get("pytest_playwright_version"),
            "browser_version": properties.get("browser_version"),
        }
    )


def _check_capture(
    path: Path,
    budgets: Mapping[str, Mapping[str, object]],
    output: dict[str, object],
    errors: list[str],
) -> None:
    try:
        probe = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"cannot read synthetic capture probe: {exc}")
        return
    budget = budgets.get("synthetic_capture", {})
    limit = float(budget.get("limit", 0))
    details = cast(Mapping[str, object], budget.get("frozen_limits", {}))
    if probe.get("temporary_filesystem") != "tmpfs":
        errors.append("synthetic capture probe did not use tmpfs")
    if probe.get("temporary_filesystem_capacity_bytes", limit + 1) > float(
        details.get("tmpfs_max_bytes", 0)
    ):
        errors.append("synthetic capture probe tmpfs exceeds its frozen capacity")
    if probe.get("temporary_filesystem_hard_limit_probe", {}).get("observed_enospc") is not True:
        errors.append("synthetic capture tmpfs hard-limit probe did not return ENOSPC")
    normal = cast(Mapping[str, object], probe.get("normal_capture", {}))
    if normal.get("trace_valid") is not True:
        errors.append("synthetic failure probe did not produce a readable trace archive")
    if normal.get("expected_failure_seen") is not True:
        errors.append("synthetic capture probe did not retain its intentional failure")
    if float(normal.get("trace_bytes", 0)) > limit:
        errors.append("synthetic failure trace exceeded its frozen per-file cap")
    if probe.get("trace_file_limit_bytes") != limit:
        errors.append("synthetic capture probe did not apply the frozen per-file cap")
    if probe.get("monitor_interval_ms") != int(details.get("monitor_interval_ms", 0)):
        errors.append("synthetic capture probe did not use the frozen monitoring interval")
    if float(normal.get("max_temporary_growth_per_sample_bytes", 0)) > float(
        details.get("max_overshoot_bytes", 0)
    ):
        errors.append("synthetic capture overshoot exceeded its frozen bound")
    overflow = cast(Mapping[str, object], probe.get("over_limit_capture", {}))
    if overflow.get("capture_limit_error_seen") is not True:
        errors.append("over-limit capture did not surface a file-size error")
    if probe.get("errors"):
        errors.append("synthetic capture probe reported errors: " + ", ".join(probe["errors"]))
    output["synthetic_capture"] = {
        "trace_bytes": normal.get("trace_bytes"),
        "limit_bytes": limit,
        "tmpfs_capacity_bytes": probe.get("temporary_filesystem_capacity_bytes"),
        "over_limit_error_visible": overflow.get("capture_limit_error_seen"),
    }


def _check_parallel(
    resource_report: Mapping[str, object],
    budgets: Mapping[str, Mapping[str, object]],
    output: dict[str, object],
    errors: list[str],
    lane: str,
) -> None:
    budget = budgets.get("parallel", {})
    details = cast(Mapping[str, object], budget.get("frozen_limits", {}))
    max_workers = float(budget.get("limit", 0))
    expected_timeout = float(
        details.get("host_timeout_seconds" if lane == "host" else "browser_timeout_seconds", 0)
    )
    expected_interval = int(
        details.get(
            "host_monitor_interval_ms" if lane == "host" else "browser_monitor_interval_ms", 0
        )
    )
    requested = resource_report.get("requested_xdist_workers")
    if not isinstance(requested, (int, float)):
        errors.append("resource report is missing its requested xdist worker count")
    elif lane == "host" and requested > max_workers:
        errors.append(f"requested xdist workers {requested} exceeds frozen {max_workers:.0f}")
    elif lane == "browser" and requested != float(details.get("browser_xdist_workers", -1)):
        errors.append(
            "browser acceptance must remain serial (xdist workers="
            f"{details.get('browser_xdist_workers', 0)})"
        )
    rss_limit = float(details.get("rss_max_bytes", 0))
    process_limit = float(details.get("process_count_max", 0))
    if float(resource_report.get("max_process_group_rss_bytes", rss_limit + 1)) > rss_limit:
        errors.append("pytest process group exceeded the frozen RSS budget")
    if float(resource_report.get("max_processes", process_limit + 1)) > process_limit:
        errors.append("pytest process group exceeded the frozen process-count budget")
    if float(resource_report.get("timeout_seconds", 0)) > expected_timeout:
        errors.append("resource monitor timeout is looser than the frozen wall-clock budget")
    if float(resource_report.get("duration_seconds", expected_timeout + 1)) > expected_timeout:
        errors.append("pytest acceptance exceeded its frozen wall-clock budget")
    if int(resource_report.get("monitor_interval_ms", 0)) != expected_interval:
        errors.append("resource monitor interval differs from its frozen interval")
    if int(resource_report.get("per_file_rlimit_bytes", 0)) != int(
        details.get("per_file_bytes", 0)
    ):
        errors.append("resource monitor per-file limit differs from its frozen cap")
    if lane == "browser":
        if resource_report.get("temporary_filesystem") != "tmpfs":
            errors.append("browser resource monitor did not run on tmpfs")
        tmpfs_limit = float(
            budgets.get("synthetic_capture", {}).get("frozen_limits", {}).get("tmpfs_max_bytes", 0)
        )
        if (
            float(resource_report.get("temporary_filesystem_capacity_bytes", tmpfs_limit + 1))
            > tmpfs_limit
        ):
            errors.append("browser temporary filesystem exceeds its frozen capacity")
        if float(resource_report.get("temporary_filesystem_limit_bytes", 0)) != tmpfs_limit:
            errors.append("browser resource monitor did not enforce the frozen tmpfs capacity")
    if resource_report.get("termination_reason") is not None:
        errors.append(
            f"resource monitor terminated the test command: {resource_report['termination_reason']}"
        )
    if int(resource_report.get("exit_code", 1)) != 0:
        errors.append(
            f"resource-wrapped acceptance command exited {resource_report.get('exit_code')}"
        )
    output["parallel_resource_report"] = dict(resource_report)


def _find_case(
    testcases: list[ElementTree.Element],
    module: str,
    name: str,
) -> ElementTree.Element | None:
    matches = [
        testcase
        for testcase in testcases
        if testcase.get("classname", "").rsplit(".", 1)[-1] == module
        and testcase.get("name", "").split("[", 1)[0] == name
    ]
    return matches[0] if len(matches) == 1 else None


def _properties(testcase: ElementTree.Element) -> dict[str, str]:
    return {
        name: value
        for node in testcase.findall("./properties/property")
        if (name := node.get("name")) is not None
        if (value := node.get("value")) is not None
    }


def _number(value: str | None, label: str, errors: list[str]) -> float | None:
    try:
        return float(value) if value is not None else None
    except ValueError:
        errors.append(f"{label} is not numeric")
        return None


def _number_list(value: str | None, label: str, errors: list[str]) -> list[float]:
    try:
        raw = json.loads(value) if value is not None else []
        if not isinstance(raw, list):
            raise ValueError
        return [float(item) for item in raw]
    except (TypeError, ValueError, json.JSONDecodeError):
        errors.append(f"{label} is not a JSON list of numbers")
        return []


def _require_samples(values: list[float], count: int, label: str, errors: list[str]) -> None:
    if count < 1 or len(values) < count:
        errors.append(f"{label} requires at least {count} measured samples; found {len(values)}")


def contract_environment() -> dict[str, object]:
    data = tomllib.loads(CONTRACT.read_text(encoding="utf-8"))
    return cast(dict[str, object], data.get("environment_inventory", {}))


if __name__ == "__main__":
    raise SystemExit(main())

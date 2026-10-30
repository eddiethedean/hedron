#!/usr/bin/env python3
"""Exercise retained and over-limit synthetic Playwright traces on bounded Linux tmpfs."""

from __future__ import annotations

import argparse
import contextlib
import errno
import json
import os
import resource
import shutil
import signal
import subprocess
import sys
import time
import uuid
import zipfile
from collections.abc import Callable
from pathlib import Path
from xml.etree import ElementTree

from run_ui_budgeted import _mount_for_path, _process_group_usage, _tree_bytes

ROOT = Path(__file__).resolve().parents[1]
PROBE_TEST = "tests/browser/test_ui_testing_capture_probe.py"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--browser", choices=("chromium", "firefox", "webkit"), required=True)
    parser.add_argument("--junit-dir", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--tempfs-limit-mib", type=int, default=128)
    parser.add_argument("--trace-file-limit-mib", type=int, default=64)
    args = parser.parse_args(argv)
    if args.tempfs_limit_mib != 128 or args.trace_file_limit_mib != 64:
        parser.error("the 1.3 capture probe requires the frozen 128 MiB tmpfs and 64 MiB file cap")

    temp_root = Path(os.environ.get("TMPDIR", "/tmp")).resolve()
    mount_type = _mount_for_path(temp_root)
    temp_stat = temp_root.stat()
    private_tmpfs = temp_stat.st_uid == os.getuid() and temp_stat.st_mode & 0o077 == 0
    stat = os.statvfs(temp_root)
    capacity_bytes = stat.f_blocks * stat.f_frsize
    limit_bytes = args.tempfs_limit_mib * 1024 * 1024
    errors: list[str] = []
    if not sys.platform.startswith("linux"):
        errors.append("synthetic capture resource probe requires Linux")
    if mount_type != "tmpfs":
        errors.append(f"TMPDIR must be tmpfs; found {mount_type!r}")
    if not private_tmpfs:
        errors.append("TMPDIR must be owned by the current user and inaccessible to group/others")
    if capacity_bytes > limit_bytes:
        errors.append(f"tmpfs capacity {capacity_bytes} exceeds frozen cap {limit_bytes}")

    storage_probe = _probe_tmpfs_hard_limit(temp_root, capacity_bytes)
    if not storage_probe["observed_enospc"]:
        errors.append("tmpfs hard-limit probe did not receive ENOSPC")

    run_id = uuid.uuid4().hex[:12]
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    threshold_root = _private_probe_root(temp_root, f"threshold-{run_id}")
    try:
        threshold_termination = _probe_soft_limit_termination(
            temp_root=threshold_root,
            output_dir=args.output_json.parent,
            run_id=run_id,
            tempfs_limit_mib=args.tempfs_limit_mib,
            file_limit_mib=args.trace_file_limit_mib,
        )
    finally:
        shutil.rmtree(threshold_root, ignore_errors=True)
    if threshold_termination["termination_reason"] != "temporary_storage_limit":
        errors.append("temporary-storage threshold probe did not terminate at its frozen limit")
    if threshold_termination["process_terminated"] is not True:
        errors.append("temporary-storage threshold probe did not terminate its writer process")
    if threshold_termination["overshoot_within_bound"] is not True:
        errors.append("temporary-storage threshold probe exceeded the frozen overshoot bound")

    normal_root = _private_probe_root(temp_root, f"normal-{run_id}")
    try:
        normal = _run_capture_case(
            browser=args.browser,
            temp_root=normal_root,
            junit_path=args.junit_dir / f"ui-capture-{args.browser}-{run_id}.xml",
            output_dir=normal_root / "output",
            artifact_dir=normal_root / "structured",
            tempfs_limit_mib=args.tempfs_limit_mib,
            file_limit_bytes=args.trace_file_limit_mib * 1024 * 1024,
        )
    finally:
        shutil.rmtree(normal_root, ignore_errors=True)
    if normal["expected_failure_seen"] is not True:
        errors.append("normal capture probe did not retain the intentional test failure")
    if not normal["trace_valid"]:
        errors.append("normal capture probe did not retain one valid trace archive")
    if int(normal["trace_bytes"]) > args.trace_file_limit_mib * 1024 * 1024:
        errors.append("normal trace exceeded the frozen per-file resource limit")
    if normal["termination_reason"] is not None:
        errors.append("normal capture probe was terminated by a resource limit")
    if normal["temporary_filesystem_usage_limit_bytes"] != 64 * 1024 * 1024:
        errors.append("normal capture probe did not enforce the frozen total-tree limit")

    overflow_root = _private_probe_root(temp_root, f"overflow-{run_id}")
    try:
        overflow = _run_capture_case(
            browser=args.browser,
            temp_root=overflow_root,
            junit_path=None,
            output_dir=overflow_root / "output",
            artifact_dir=overflow_root / "structured",
            tempfs_limit_mib=args.tempfs_limit_mib,
            file_limit_bytes=1024,
        )
    finally:
        shutil.rmtree(overflow_root, ignore_errors=True)
    if overflow["capture_limit_error_seen"] is not True:
        errors.append("over-limit trace did not surface the operating-system file-size error")

    report = {
        "schema_version": 1,
        "lane": "synthetic-capture",
        "operating_system": "Linux",
        "python": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "browser": args.browser,
        "playwright_version": _package_version("playwright"),
        "pytest_playwright_version": _package_version("pytest-playwright"),
        "temporary_filesystem": mount_type,
        "temporary_filesystem_private": private_tmpfs,
        "temporary_filesystem_capacity_bytes": capacity_bytes,
        "temporary_filesystem_limit_bytes": limit_bytes,
        "temporary_filesystem_usage_limit_bytes": 64 * 1024 * 1024,
        "temporary_filesystem_hard_limit_probe": storage_probe,
        "storage_threshold_termination": threshold_termination,
        "monitor_interval_ms": 25,
        "trace_file_limit_bytes": args.trace_file_limit_mib * 1024 * 1024,
        "normal_capture": normal,
        "over_limit_capture": overflow,
        "errors": errors,
    }
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, sort_keys=True))
    return 1 if errors else 0


def _private_probe_root(parent: Path, name: str) -> Path:
    path = parent / f".hedron-ui-capture-{name}"
    path.mkdir(mode=0o700)
    info = path.stat()
    if path.is_symlink() or info.st_uid != os.getuid() or info.st_mode & 0o077:
        shutil.rmtree(path, ignore_errors=True)
        raise OSError("capture probe directory must be private and owned by the current user")
    return path


def _probe_tmpfs_hard_limit(root: Path, capacity_bytes: int) -> dict[str, object]:
    path = root / f".hedron-ui-space-probe-{uuid.uuid4().hex}"
    written = 0
    observed_enospc = False
    chunk = b"h" * (1024 * 1024)
    try:
        with path.open("wb", buffering=0) as stream:
            while written <= capacity_bytes:
                try:
                    count = stream.write(chunk)
                except OSError as exc:
                    if exc.errno != errno.ENOSPC:
                        raise
                    observed_enospc = True
                    break
                if count != len(chunk):
                    written += count
                    try:
                        _ = stream.write(b"x")
                    except OSError as exc:
                        if exc.errno != errno.ENOSPC:
                            raise
                        observed_enospc = True
                    break
                written += count
            stream.flush()
            os.fsync(stream.fileno())
    finally:
        path.unlink(missing_ok=True)
    return {"bytes_written_before_enospc": written, "observed_enospc": observed_enospc}


def _probe_soft_limit_termination(
    *,
    temp_root: Path,
    output_dir: Path,
    run_id: str,
    tempfs_limit_mib: int,
    file_limit_mib: int,
) -> dict[str, object]:
    soft_limit_mib = 32
    soft_limit_bytes = soft_limit_mib * 1024 * 1024
    overshoot_bound_bytes = 64 * 1024 * 1024
    output_path = output_dir / f"ui-capture-termination-{run_id}.json"
    output_dir.mkdir(parents=True, exist_ok=True)
    writer = "\n".join(
        (
            "import os",
            "from pathlib import Path",
            "root = Path(os.environ['TMPDIR']) / 'hedron-ui-soft-limit-probe'",
            "root.mkdir(exist_ok=True)",
            "chunk = b'x' * (1024 * 1024)",
            "index = 0",
            "while True:",
            "    path = root / f'{index % 8}.bin'",
            "    with path.open('wb', buffering=0) as stream:",
            "        for _ in range(8):",
            "            stream.write(chunk)",
            "    index += 1",
        )
    )
    command = [
        sys.executable,
        str(ROOT / "scripts/run_ui_budgeted.py"),
        "--output-json",
        str(output_path),
        "--timeout-seconds",
        "60",
        "--max-rss-mib",
        "1024",
        "--max-processes",
        "16",
        "--sample-interval-ms",
        "25",
        "--tempfs-limit-mib",
        str(tempfs_limit_mib),
        "--tempfs-usage-limit-mib",
        str(soft_limit_mib),
        "--max-file-mib",
        str(file_limit_mib),
        "--",
        sys.executable,
        "-c",
        writer,
    ]
    environment = os.environ.copy()
    environment["TMPDIR"] = str(temp_root)
    completed = subprocess.run(
        command,
        cwd=ROOT,
        env=environment,
        capture_output=True,
        timeout=70,
        check=False,
    )
    try:
        resource_report = json.loads(output_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        resource_report = {"report_error": str(exc)}
    finally:
        shutil.rmtree(temp_root / "hedron-ui-soft-limit-probe", ignore_errors=True)
    if not isinstance(resource_report, dict):
        resource_report = {"report_error": "runner output was not a JSON object"}
    max_temp_bytes = int(resource_report.get("max_temporary_tree_bytes", 0))
    max_growth_bytes = int(resource_report.get("max_temporary_growth_per_sample_bytes", 0))
    termination_reason = resource_report.get("termination_reason")
    return {
        "wrapper_exit_code": completed.returncode,
        "exit_code": resource_report.get("exit_code"),
        "termination_reason": termination_reason,
        "max_temporary_tree_bytes": max_temp_bytes,
        "max_temporary_growth_per_sample_bytes": max_growth_bytes,
        "monitor_interval_ms": resource_report.get("monitor_interval_ms"),
        "soft_limit_bytes": resource_report.get("temporary_filesystem_usage_limit_bytes"),
        "overshoot_bound_bytes": overshoot_bound_bytes,
        "process_terminated": completed.returncode == 1
        and isinstance(resource_report.get("exit_code"), int)
        and int(resource_report["exit_code"]) < 0,
        "overshoot_within_bound": soft_limit_bytes
        < max_temp_bytes
        <= soft_limit_bytes + overshoot_bound_bytes
        and max_growth_bytes <= overshoot_bound_bytes,
    }


def _run_capture_case(
    *,
    browser: str,
    temp_root: Path,
    junit_path: Path | None,
    output_dir: Path,
    artifact_dir: Path,
    tempfs_limit_mib: int,
    file_limit_bytes: int,
) -> dict[str, object]:
    pytest_command = [
        sys.executable,
        "-m",
        "pytest",
        "-q",
        "-n",
        "0",
        "--browser",
        browser,
        "--tracing",
        "retain-on-failure",
        "--output",
        str(output_dir),
        "--hedron-ui-artifacts",
        str(artifact_dir),
    ]
    if junit_path is not None:
        pytest_command.append(f"--junitxml={junit_path}")
    pytest_command.append(PROBE_TEST)
    environment = os.environ.copy()
    environment["TMPDIR"] = str(temp_root)
    environment["HEDRON_BROWSER"] = "1"
    environment["HEDRON_BROWSER_ENGINE"] = browser
    environment["HEDRON_UI_CAPTURE_PROBE_FAIL"] = "1"
    environment.pop("HEDRON_UI_CAPTURE_BUDGET", None)
    resource_report_path = output_dir.parent / f"{output_dir.name}-resources.json"
    uses_budget_runner = file_limit_bytes == 64 * 1024 * 1024
    if uses_budget_runner:
        command = [
            sys.executable,
            str(ROOT / "scripts/run_ui_budgeted.py"),
            "--output-json",
            str(resource_report_path),
            "--timeout-seconds",
            "180",
            "--max-rss-mib",
            "8192",
            "--max-processes",
            "64",
            "--sample-interval-ms",
            "25",
            "--tempfs-limit-mib",
            str(tempfs_limit_mib),
            "--tempfs-usage-limit-mib",
            "64",
            "--max-file-mib",
            "64",
            "--",
            *pytest_command,
        ]
    else:
        command = pytest_command
        environment["HEDRON_UI_CAPTURE_BUDGET"] = "linux-tmpfs-128m-monitor-25ms-file-64m-v1"

    def apply_file_limit() -> None:
        resource.setrlimit(resource.RLIMIT_FSIZE, (file_limit_bytes, file_limit_bytes))

    preexec: Callable[[], None] | None = None if uses_budget_runner else apply_file_limit

    started = time.monotonic()
    process = subprocess.Popen(
        command,
        cwd=ROOT,
        env=environment,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        start_new_session=True,
        preexec_fn=preexec,
    )
    peak_temp_bytes = 0
    peak_rss = 0
    peak_processes = 0
    max_temp_delta = 0
    previous_temp_bytes = 0
    timed_out = False
    while process.poll() is None:
        temp_bytes = _tree_bytes(temp_root)
        rss_bytes, processes = _process_group_usage(process.pid)
        peak_temp_bytes = max(peak_temp_bytes, temp_bytes)
        peak_rss = max(peak_rss, rss_bytes)
        peak_processes = max(peak_processes, processes)
        max_temp_delta = max(max_temp_delta, temp_bytes - previous_temp_bytes)
        previous_temp_bytes = temp_bytes
        if time.monotonic() - started > (240 if uses_budget_runner else 180):
            timed_out = True
            _kill_process_group(process)
            break
        time.sleep(0.025)
    stdout, _ = process.communicate(timeout=5)
    junit = _read_junit(junit_path) if junit_path is not None else None
    testcase = next(iter(junit.iter("testcase")), None) if junit is not None else None
    outcome_text = "\n".join(
        child.text or ""
        for child in (() if testcase is None else testcase)
        if child.tag in {"failure", "error"}
    )
    output = (stdout or b"").decode("utf-8", errors="replace")
    details = outcome_text + "\n" + output
    traces = list(output_dir.rglob("trace.zip")) if output_dir.exists() else []
    trace_bytes = traces[0].stat().st_size if len(traces) == 1 else 0
    trace_valid = len(traces) == 1 and zipfile.is_zipfile(traces[0])
    expected_failure_seen = (
        testcase is not None
        and testcase.find("failure") is not None
        and "intentional synthetic capture budget probe" in details
    )
    capture_limit_error_seen = any(
        marker in details.lower() for marker in ("file too large", "file size", "errno 27", "efbig")
    )
    if uses_budget_runner:
        try:
            resource_report = json.loads(resource_report_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            resource_report = {}
        if isinstance(resource_report, dict):
            peak_temp_bytes = max(
                peak_temp_bytes,
                int(resource_report.get("max_temporary_tree_bytes", 0)),
            )
            max_temp_delta = max(
                max_temp_delta,
                int(resource_report.get("max_temporary_growth_per_sample_bytes", 0)),
            )
            peak_rss = int(resource_report.get("max_process_group_rss_bytes", peak_rss))
            peak_processes = int(resource_report.get("max_processes", peak_processes))
            termination_reason = resource_report.get("termination_reason")
            usage_limit_bytes = resource_report.get("temporary_filesystem_usage_limit_bytes")
        else:
            termination_reason = "invalid_resource_report"
            usage_limit_bytes = None
    else:
        termination_reason = None
        usage_limit_bytes = None
    report = {
        "exit_code": process.returncode,
        "duration_seconds": round(time.monotonic() - started, 6),
        "timed_out": timed_out,
        "max_temporary_tree_bytes": peak_temp_bytes,
        "max_temporary_growth_per_sample_bytes": max_temp_delta,
        "monitor_interval_ms": 25,
        "max_process_group_rss_bytes": peak_rss,
        "max_processes": peak_processes,
        "file_limit_bytes": file_limit_bytes,
        "trace_count": len(traces),
        "trace_bytes": trace_bytes,
        "trace_valid": trace_valid,
        "expected_failure_seen": expected_failure_seen,
        "capture_limit_error_seen": capture_limit_error_seen,
        "termination_reason": termination_reason,
        "temporary_filesystem_usage_limit_bytes": usage_limit_bytes,
        "junit_path": str(junit_path) if junit_path is not None else None,
        "resource_report_path": str(resource_report_path) if uses_budget_runner else None,
    }
    shutil.rmtree(output_dir, ignore_errors=True)
    shutil.rmtree(artifact_dir, ignore_errors=True)
    if uses_budget_runner:
        resource_report_path.unlink(missing_ok=True)
    return report


def _read_junit(path: Path) -> ElementTree.Element | None:
    try:
        return ElementTree.parse(path).getroot()
    except (OSError, ElementTree.ParseError):
        return None


def _kill_process_group(process: subprocess.Popen[bytes]) -> None:
    with contextlib.suppress(ProcessLookupError):
        os.killpg(process.pid, signal.SIGTERM)
    try:
        _ = process.wait(timeout=2)
    except subprocess.TimeoutExpired:
        with contextlib.suppress(ProcessLookupError):
            os.killpg(process.pid, signal.SIGKILL)


def _package_version(package: str) -> str:
    from importlib.metadata import version

    return version(package)


if __name__ == "__main__":
    raise SystemExit(main())

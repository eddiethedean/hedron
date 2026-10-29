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

    temp_root = Path(os.environ.get("TMPDIR", "/tmp")).resolve()
    mount_type = _mount_for_path(temp_root)
    stat = os.statvfs(temp_root)
    capacity_bytes = stat.f_blocks * stat.f_frsize
    limit_bytes = args.tempfs_limit_mib * 1024 * 1024
    errors: list[str] = []
    if not sys.platform.startswith("linux"):
        errors.append("synthetic capture resource probe requires Linux")
    if mount_type != "tmpfs":
        errors.append(f"TMPDIR must be tmpfs; found {mount_type!r}")
    if capacity_bytes > limit_bytes:
        errors.append(f"tmpfs capacity {capacity_bytes} exceeds frozen cap {limit_bytes}")

    storage_probe = _probe_tmpfs_hard_limit(temp_root, capacity_bytes)
    if not storage_probe["observed_enospc"]:
        errors.append("tmpfs hard-limit probe did not receive ENOSPC")

    run_id = uuid.uuid4().hex[:12]
    normal = _run_capture_case(
        browser=args.browser,
        temp_root=temp_root,
        junit_path=args.junit_dir / f"ui-capture-{args.browser}-{run_id}.xml",
        output_dir=temp_root / f"output-normal-{run_id}",
        artifact_dir=temp_root / f"structured-normal-{run_id}",
        file_limit_bytes=args.trace_file_limit_mib * 1024 * 1024,
    )
    if normal["expected_failure_seen"] is not True:
        errors.append("normal capture probe did not retain the intentional test failure")
    if not normal["trace_valid"]:
        errors.append("normal capture probe did not retain one valid trace archive")
    if int(normal["trace_bytes"]) > args.trace_file_limit_mib * 1024 * 1024:
        errors.append("normal trace exceeded the frozen per-file resource limit")

    overflow = _run_capture_case(
        browser=args.browser,
        temp_root=temp_root,
        junit_path=None,
        output_dir=temp_root / f"output-overflow-{run_id}",
        artifact_dir=temp_root / f"structured-overflow-{run_id}",
        file_limit_bytes=1024,
    )
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
        "temporary_filesystem_capacity_bytes": capacity_bytes,
        "temporary_filesystem_limit_bytes": limit_bytes,
        "temporary_filesystem_hard_limit_probe": storage_probe,
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


def _run_capture_case(
    *,
    browser: str,
    temp_root: Path,
    junit_path: Path | None,
    output_dir: Path,
    artifact_dir: Path,
    file_limit_bytes: int,
) -> dict[str, object]:
    command = [
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
        command.append(f"--junitxml={junit_path}")
    command.append(PROBE_TEST)
    environment = os.environ.copy()
    environment["HEDRON_BROWSER"] = "1"
    environment["HEDRON_BROWSER_ENGINE"] = browser
    environment["HEDRON_UI_CAPTURE_PROBE_FAIL"] = "1"

    def apply_file_limit() -> None:
        resource.setrlimit(resource.RLIMIT_FSIZE, (file_limit_bytes, file_limit_bytes))

    started = time.monotonic()
    process = subprocess.Popen(
        command,
        cwd=ROOT,
        env=environment,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        start_new_session=True,
        preexec_fn=apply_file_limit,
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
        if time.monotonic() - started > 180:
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
        "junit_path": str(junit_path) if junit_path is not None else None,
    }
    shutil.rmtree(output_dir, ignore_errors=True)
    shutil.rmtree(artifact_dir, ignore_errors=True)
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

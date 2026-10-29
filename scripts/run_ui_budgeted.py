#!/usr/bin/env python3
"""Run one Linux UI-test command under measured time, memory, process, and temp budgets."""

from __future__ import annotations

import argparse
import contextlib
import json
import os
import platform
import resource
import signal
import subprocess
import sys
import time
from pathlib import Path

_CAPTURE_BUDGET_ENV = "HEDRON_UI_CAPTURE_BUDGET"
_CAPTURE_BUDGET_VALUE = "linux-tmpfs-128m-monitor-25ms-file-64m-v1"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--timeout-seconds", type=float, default=900)
    parser.add_argument("--max-rss-mib", type=int, default=8192)
    parser.add_argument("--max-processes", type=int, default=64)
    parser.add_argument("--sample-interval-ms", type=int, default=50)
    parser.add_argument("--tempfs-limit-mib", type=int)
    parser.add_argument("--tempfs-usage-limit-mib", type=int)
    parser.add_argument("--max-file-mib", type=int, default=64)
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args(argv)

    if not sys.platform.startswith("linux"):
        parser.error("the frozen UI resource budgets require Linux")
    command = args.command[1:] if args.command[:1] == ["--"] else args.command
    if not command:
        parser.error("a command must follow --")
    if args.timeout_seconds <= 0 or args.max_rss_mib <= 0 or args.max_processes <= 0:
        parser.error("time, memory, and process limits must be positive")
    if args.sample_interval_ms < 10 or args.max_file_mib <= 0:
        parser.error("sample interval must be at least 10ms and file limit must be positive")

    temp_root = Path(os.environ.get("TMPDIR", "/tmp")).resolve()
    temp_mount = _mount_for_path(temp_root)
    temp_stat = temp_root.stat()
    private_temp = temp_stat.st_uid == os.getuid() and temp_stat.st_mode & 0o077 == 0
    temp_capacity = os.statvfs(temp_root).f_blocks * os.statvfs(temp_root).f_frsize
    if args.tempfs_limit_mib is not None:
        if temp_mount != "tmpfs":
            parser.error(f"TMPDIR must be a bounded tmpfs mount; found {temp_mount!r}")
        if not private_temp:
            parser.error(
                "TMPDIR must be owned by the current user and inaccessible to group/others"
            )
        temp_limit_bytes = args.tempfs_limit_mib * 1024 * 1024
        if temp_capacity > temp_limit_bytes:
            parser.error(
                f"TMPDIR capacity {temp_capacity} exceeds the frozen {temp_limit_bytes} byte cap"
            )
    else:
        temp_limit_bytes = None
    if args.tempfs_usage_limit_mib is not None:
        if temp_limit_bytes is None:
            parser.error("--tempfs-usage-limit-mib requires --tempfs-limit-mib")
        if args.tempfs_usage_limit_mib <= 0:
            parser.error("temporary storage usage limit must be positive")
        temp_usage_limit_bytes = args.tempfs_usage_limit_mib * 1024 * 1024
        if temp_usage_limit_bytes > temp_limit_bytes:
            parser.error("temporary storage usage limit cannot exceed the tmpfs capacity limit")
    else:
        temp_usage_limit_bytes = None

    child_env = os.environ.copy()
    # Never inherit a caller-supplied assertion. Mark the child only when this
    # wrapper is enforcing the frozen raw-capture envelope itself.
    child_env.pop(_CAPTURE_BUDGET_ENV, None)
    if (
        temp_mount == "tmpfs"
        and private_temp
        and temp_limit_bytes == 128 * 1024 * 1024
        and temp_usage_limit_bytes == 64 * 1024 * 1024
        and args.sample_interval_ms == 25
        and args.max_file_mib == 64
    ):
        child_env[_CAPTURE_BUDGET_ENV] = _CAPTURE_BUDGET_VALUE

    start = time.monotonic()
    process = subprocess.Popen(
        command,
        env=child_env,
        start_new_session=True,
        preexec_fn=_file_size_limit(args.max_file_mib),
    )
    peak_rss = 0
    peak_processes = 0
    peak_temp_bytes = 0
    max_temp_delta = 0
    previous_temp_bytes = 0
    sample_count = 0
    termination_reason: str | None = None

    while True:
        rss, process_count = _process_group_usage(process.pid)
        temp_bytes = _tree_bytes(temp_root)
        peak_rss = max(peak_rss, rss)
        peak_processes = max(peak_processes, process_count)
        peak_temp_bytes = max(peak_temp_bytes, temp_bytes)
        max_temp_delta = max(max_temp_delta, temp_bytes - previous_temp_bytes)
        previous_temp_bytes = temp_bytes
        sample_count += 1
        elapsed = time.monotonic() - start
        if termination_reason is None:
            if elapsed > args.timeout_seconds:
                termination_reason = "wall_clock_limit"
            elif rss > args.max_rss_mib * 1024 * 1024:
                termination_reason = "process_group_rss_limit"
            elif process_count > args.max_processes:
                termination_reason = "process_count_limit"
            elif temp_usage_limit_bytes is not None and temp_bytes > temp_usage_limit_bytes:
                termination_reason = "temporary_storage_limit"
        if termination_reason is not None:
            _terminate_group(process.pid, process)
            break
        return_code = process.poll()
        if return_code is not None and process_count <= 1:
            break
        if return_code is not None and elapsed > args.timeout_seconds:
            termination_reason = "orphaned_process_group_timeout"
            _terminate_group(process.pid, process)
            break
        time.sleep(args.sample_interval_ms / 1000)

    return_code = process.wait()
    duration = time.monotonic() - start
    report = {
        "schema_version": 1,
        "operating_system": "Linux",
        "architecture": platform.machine(),
        "python": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "command": command,
        "duration_seconds": round(duration, 6),
        "timeout_seconds": args.timeout_seconds,
        "max_process_group_rss_bytes": peak_rss,
        "max_processes": peak_processes,
        "max_temporary_tree_bytes": peak_temp_bytes,
        "max_temporary_growth_per_sample_bytes": max_temp_delta,
        "temporary_filesystem": temp_mount,
        "temporary_filesystem_capacity_bytes": temp_capacity,
        "temporary_filesystem_limit_bytes": temp_limit_bytes,
        "temporary_filesystem_usage_limit_bytes": temp_usage_limit_bytes,
        "monitor_interval_ms": args.sample_interval_ms,
        "sample_count": sample_count,
        "per_file_rlimit_bytes": args.max_file_mib * 1024 * 1024,
        "termination_reason": termination_reason,
        "exit_code": return_code,
        "requested_xdist_workers": _requested_workers(command),
    }
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, sort_keys=True))
    if termination_reason is not None:
        print(
            f"error: UI test command terminated at resource budget {termination_reason}",
            file=sys.stderr,
        )
        return 1
    return return_code


def _file_size_limit(max_file_mib: int):
    limit = max_file_mib * 1024 * 1024

    def apply() -> None:
        resource.setrlimit(resource.RLIMIT_FSIZE, (limit, limit))

    return apply


def _requested_workers(command: list[str]) -> int | str:
    for index, argument in enumerate(command[:-1]):
        if argument in {"-n", "--numprocesses"}:
            value = command[index + 1]
            return int(value) if value.isdecimal() else value
    value = os.environ.get("PYTEST_XDIST_AUTO_NUM_WORKERS", "auto")
    return int(value) if value.isdecimal() else value


def _mount_for_path(path: Path) -> str:
    best_match = "unknown"
    best_length = -1
    for line in Path("/proc/self/mountinfo").read_text(encoding="utf-8").splitlines():
        left, separator, right = line.partition(" - ")
        if not separator:
            continue
        fields = left.split()
        if len(fields) < 5:
            continue
        mount_point = Path(fields[4].replace("\\040", " ")).resolve()
        try:
            _ = path.relative_to(mount_point)
        except ValueError:
            continue
        if len(str(mount_point)) > best_length:
            best_match = right.split()[0]
            best_length = len(str(mount_point))
    return best_match


def _process_group_usage(group_id: int) -> tuple[int, int]:
    page_size = os.sysconf("SC_PAGE_SIZE")
    resident_bytes = 0
    process_count = 0
    for entry in Path("/proc").iterdir():
        if not entry.name.isdecimal():
            continue
        try:
            stat_line = (entry / "stat").read_text(encoding="ascii")
            closing_paren = stat_line.rfind(")")
            fields = stat_line[closing_paren + 2 :].split()
            if int(fields[2]) != group_id:
                continue
            resident_pages = int((entry / "statm").read_text(encoding="ascii").split()[1])
        except (OSError, IndexError, ValueError):
            continue
        resident_bytes += resident_pages * page_size
        process_count += 1
    return resident_bytes, process_count


def _tree_bytes(root: Path) -> int:
    total = 0
    if not root.exists():
        return 0
    for current, directories, files in os.walk(root, followlinks=False):
        current_path = Path(current)
        for name in (*directories, *files):
            candidate = current_path / name
            try:
                info = candidate.lstat()
            except OSError:
                continue
            if candidate.is_symlink():
                continue
            total += getattr(info, "st_blocks", 0) * 512 or info.st_size
    return total


def _terminate_group(group_id: int, process: subprocess.Popen[bytes]) -> None:
    with contextlib.suppress(ProcessLookupError):
        os.killpg(group_id, signal.SIGTERM)
    try:
        _ = process.wait(timeout=2)
    except subprocess.TimeoutExpired:
        with contextlib.suppress(ProcessLookupError):
            os.killpg(group_id, signal.SIGKILL)


if __name__ == "__main__":
    raise SystemExit(main())

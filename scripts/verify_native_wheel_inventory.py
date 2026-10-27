#!/usr/bin/env python3
"""Require the full CPython 3.11–3.14 native wheel matrix."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import subprocess
import sys
import tomllib
from pathlib import Path

from packaging.utils import canonicalize_name, parse_wheel_filename
from packaging.version import Version

ROOT = Path(__file__).resolve().parents[1]
PYTHON_TAGS = ("cp311", "cp312", "cp313", "cp314")
PLATFORM_TAGS: dict[str, frozenset[str]] = {
    "linux-x86_64": frozenset({"manylinux_2_17_x86_64", "manylinux2014_x86_64"}),
    "linux-aarch64": frozenset({"manylinux_2_17_aarch64", "manylinux2014_aarch64"}),
    "macos-arm64": frozenset({"macosx_11_0_arm64"}),
    "windows-amd64": frozenset({"win_amd64"}),
}


def expected_version() -> Version:
    pyproject = tomllib.loads(
        (ROOT / "packages/hedron-native/pyproject.toml").read_text(encoding="utf-8")
    )
    project = pyproject.get("project")
    if not isinstance(project, dict) or not isinstance(project.get("version"), str):
        raise ValueError("hedron-native pyproject.toml has no project.version")
    return Version(project["version"])


def read_wheel(path: Path, version: Version) -> tuple[set[str], set[str]]:
    name, wheel_version, _build, tags = parse_wheel_filename(path.name)
    if canonicalize_name(name) != "hedron-native":
        raise ValueError(f"unexpected distribution in {path.name}")
    if wheel_version != version:
        raise ValueError(f"{path.name} has version {wheel_version}; expected {version}")
    interpreters = {tag.interpreter for tag in tags}
    abis = {tag.abi for tag in tags}
    platforms = {tag.platform for tag in tags}
    if len(interpreters) != 1 or len(abis) != 1:
        raise ValueError(f"{path.name} has a non-specific interpreter or ABI tag")
    interpreter = next(iter(interpreters))
    if interpreter not in PYTHON_TAGS or abis != {interpreter}:
        raise ValueError(f"{path.name} is outside the supported CPython wheel matrix")
    return {interpreter}, platforms


def verify_platform(
    wheel_paths: list[Path], *, platform_name: str, version: Version
) -> list[dict[str, str]]:
    expected_platform_tags = PLATFORM_TAGS[platform_name]
    rows: list[dict[str, str]] = []
    seen_python_tags: set[str] = set()
    for path in wheel_paths:
        interpreters, platforms = read_wheel(path, version)
        if not platforms or not platforms <= expected_platform_tags:
            raise ValueError(
                f"{path.name} has platform tags {sorted(platforms)}; "
                f"expected {sorted(expected_platform_tags)}"
            )
        interpreter = next(iter(interpreters))
        if interpreter in seen_python_tags:
            raise ValueError(f"duplicate {interpreter} wheel for {platform_name}")
        seen_python_tags.add(interpreter)
        rows.append(
            {
                "name": path.name,
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            }
        )
    if seen_python_tags != set(PYTHON_TAGS):
        missing = sorted(set(PYTHON_TAGS) - seen_python_tags)
        extra = sorted(seen_python_tags - set(PYTHON_TAGS))
        raise ValueError(
            f"{platform_name} wheel matrix incomplete; missing={missing}, unexpected={extra}"
        )
    return sorted(rows, key=lambda row: row["name"])


def platform_for_wheel(path: Path, version: Version) -> str:
    _interpreters, platforms = read_wheel(path, version)
    matches = [name for name, tags in PLATFORM_TAGS.items() if platforms <= tags]
    if len(matches) != 1:
        raise ValueError(f"{path.name} does not match exactly one supported platform")
    return matches[0]


def collect_inventory(
    wheel_dir: Path, *, platform_name: str | None, version: Version
) -> dict[str, object]:
    wheels = sorted(wheel_dir.glob("hedron_native-*.whl"))
    if not wheels:
        raise ValueError(f"no hedron-native wheels found in {wheel_dir}")
    if platform_name is not None:
        rows = verify_platform(wheels, platform_name=platform_name, version=version)
        if len(rows) != len(wheels):
            raise ValueError(f"{wheel_dir} contains wheels outside {platform_name}")
        return {"platform": platform_name, "wheels": rows}

    grouped: dict[str, list[Path]] = {name: [] for name in PLATFORM_TAGS}
    for wheel in wheels:
        grouped[platform_for_wheel(wheel, version)].append(wheel)
    platforms = {
        name: verify_platform(group, platform_name=name, version=version)
        for name, group in grouped.items()
    }
    if len(wheels) != len(PYTHON_TAGS) * len(PLATFORM_TAGS):
        raise ValueError(
            "combined native wheel matrix must contain exactly "
            f"{len(PYTHON_TAGS) * len(PLATFORM_TAGS)} wheels; found {len(wheels)}"
        )
    return {"platforms": platforms}


def source_commit() -> str:
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("wheel_dir", type=Path)
    parser.add_argument("--platform", choices=tuple(PLATFORM_TAGS))
    parser.add_argument("--all-platforms", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    if (args.platform is None and not args.all_platforms) or (
        args.platform is not None and args.all_platforms
    ):
        parser.error("select exactly one of --platform or --all-platforms")
    try:
        version = expected_version()
        inventory = collect_inventory(
            args.wheel_dir.resolve(), platform_name=args.platform, version=version
        )
        server_url = os.environ.get("GITHUB_SERVER_URL")
        repository = os.environ.get("GITHUB_REPOSITORY")
        run_id = os.environ.get("GITHUB_RUN_ID")
        workflow_run = (
            f"{server_url}/{repository}/actions/runs/{run_id}"
            if server_url is not None and repository is not None and run_id is not None
            else None
        )
        evidence: dict[str, object] = {
            "schema": "hedron.native-wheel-inventory/1",
            "source_commit": source_commit(),
            "package": "hedron-native",
            "version": str(version),
            "python_tags": list(PYTHON_TAGS),
            "platform": platform.platform(),
            "architecture": platform.machine(),
            "workflow_run": workflow_run,
            **inventory,
        }
    except (OSError, ValueError, subprocess.CalledProcessError) as exc:
        print(f"native wheel inventory failed: {exc}", file=sys.stderr)
        return 1

    serialized = json.dumps(evidence, indent=2, sort_keys=True) + "\n"
    if args.output is None:
        print(serialized, end="")
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(serialized, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

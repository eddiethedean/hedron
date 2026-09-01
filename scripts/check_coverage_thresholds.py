#!/usr/bin/env python3
"""Enforce independent branch-aware coverage floors from coverage.py JSON."""

from __future__ import annotations

import argparse
import json
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import cast


@dataclass(frozen=True, slots=True)
class PackageCoverage:
    name: str
    covered: int
    total: int

    @property
    def percent(self) -> float:
        return 100.0 if self.total == 0 else self.covered * 100.0 / self.total


def _integer(summary: Mapping[str, object], key: str) -> int:
    value = summary.get(key)
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"coverage summary field {key!r} must be a non-negative integer")
    return value


def package_coverage(
    report: Mapping[str, object], *, name: str, source_prefix: str
) -> PackageCoverage:
    raw_files = report.get("files")
    if not isinstance(raw_files, Mapping):
        raise ValueError("coverage report requires a files mapping")
    files = cast(Mapping[object, object], raw_files)
    covered = 0
    total = 0
    matched = 0
    normalized_prefix = source_prefix.replace("\\", "/").rstrip("/") + "/"
    for raw_path, raw_payload in files.items():
        path = str(raw_path).replace("\\", "/")
        if not path.startswith(normalized_prefix) or not isinstance(raw_payload, Mapping):
            continue
        payload = cast(Mapping[str, object], raw_payload)
        raw_summary = payload.get("summary")
        if not isinstance(raw_summary, Mapping):
            raise ValueError(f"coverage file {path!r} requires a summary mapping")
        summary = cast(Mapping[str, object], raw_summary)
        statements = _integer(summary, "num_statements")
        branches = _integer(summary, "num_branches")
        covered_lines = _integer(summary, "covered_lines")
        covered_branches = _integer(summary, "covered_branches")
        covered += covered_lines + covered_branches
        total += statements + branches
        matched += 1
    if matched == 0:
        raise ValueError(f"coverage report contains no files under {source_prefix!r}")
    return PackageCoverage(name=name, covered=covered, total=total)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report", type=Path)
    parser.add_argument("--hedron", type=float, default=73.0, dest="hedron_floor")
    parser.add_argument("--hedron-core", type=float, default=83.0, dest="core_floor")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    raw: object = json.loads(args.report.read_text(encoding="utf-8"))
    if not isinstance(raw, Mapping):
        raise SystemExit("coverage report must contain a JSON object")
    report = cast(Mapping[str, object], raw)
    checks = (
        (
            package_coverage(
                report,
                name="hedron",
                source_prefix="packages/hedron/src/hedron",
            ),
            args.hedron_floor,
        ),
        (
            package_coverage(
                report,
                name="hedron-core",
                source_prefix="packages/hedron-core/src/hedron_core",
            ),
            args.core_floor,
        ),
    )
    failed = False
    for result, floor in checks:
        print(
            f"{result.name}: {result.percent:.2f}% "
            f"({result.covered}/{result.total}; floor {floor:.2f}%)"
        )
        failed = result.percent + 1e-12 < floor or failed
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())

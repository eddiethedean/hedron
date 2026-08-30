#!/usr/bin/env python3
"""Ensure every workspace Python package is covered by the strict typing gate."""

from __future__ import annotations

import re
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CI_CHECKS = ROOT / "scripts/ci_checks.sh"
PACKAGE_ROOT_PATTERN = re.compile(
    r"^\s+(packages/[A-Za-z0-9_.-]+/src/[A-Za-z0-9_]+)\s*\\?\s*$"
)


def _workspace_package_roots() -> set[str]:
    workspace = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    members = workspace["tool"]["uv"]["workspace"]["members"]
    roots: set[str] = set()
    errors: list[str] = []

    for member in members:
        member_path = ROOT / member
        project_path = member_path / "pyproject.toml"
        if not project_path.is_file():
            errors.append(f"{member}: missing pyproject.toml")
            continue
        project = tomllib.loads(project_path.read_text(encoding="utf-8"))["project"]
        distribution = str(project["name"])
        import_name = distribution.replace("-", "_").replace(".", "_")
        package_path = member_path / "src" / import_name
        relative = package_path.relative_to(ROOT).as_posix()
        if not (package_path / "__init__.py").is_file():
            errors.append(f"{member}: expected Python package root {relative}")
            continue
        roots.add(relative)

    if errors:
        raise ValueError("\n".join(errors))
    return roots


def _strict_gate_package_roots() -> set[str]:
    source = CI_CHECKS.read_text(encoding="utf-8")
    start_marker = "quality_strict_package_types() {"
    start = source.find(start_marker)
    if start < 0:
        raise ValueError(f"{CI_CHECKS.relative_to(ROOT)} has no strict typing function")
    end = source.find("\n}", start)
    if end < 0:
        raise ValueError(
            f"{CI_CHECKS.relative_to(ROOT)} has an unterminated strict typing function"
        )

    roots = {
        match.group(1)
        for line in source[start:end].splitlines()
        if (match := PACKAGE_ROOT_PATTERN.match(line))
    }
    if not roots:
        raise ValueError("strict typing function has no package roots")
    return roots


def main() -> int:
    try:
        workspace_roots = _workspace_package_roots()
        strict_gate_roots = _strict_gate_package_roots()
    except (OSError, KeyError, TypeError, tomllib.TOMLDecodeError, ValueError) as exc:
        print(f"package typing inventory error: {exc}", file=sys.stderr)
        return 1

    missing = sorted(workspace_roots - strict_gate_roots)
    stale = sorted(strict_gate_roots - workspace_roots)
    if missing or stale:
        if missing:
            print("Missing from strict package typing gate:", file=sys.stderr)
            for root in missing:
                print(f"  {root}", file=sys.stderr)
        if stale:
            print("Strict package typing gate contains non-workspace roots:", file=sys.stderr)
            for root in stale:
                print(f"  {root}", file=sys.stderr)
        return 1

    print(f"package typing inventory: {len(workspace_roots)} workspace packages covered")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

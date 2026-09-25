#!/usr/bin/env python3
"""Enforce the workspace's package checker coverage and explicit Any ban."""

from __future__ import annotations

import ast
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "pyproject.toml"
PYTHON_ROOTS = ("examples", "packages", "scripts", "tests", "typings")


def _explicit_any_uses() -> list[str]:
    failures: list[str] = []
    for root_name in PYTHON_ROOTS:
        root = ROOT / root_name
        if not root.is_dir():
            continue
        paths = sorted((*root.rglob("*.py"), *root.rglob("*.pyi")))
        for path in paths:
            try:
                tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            except (OSError, SyntaxError) as exc:
                failures.append(f"{path.relative_to(ROOT)}: cannot inspect Python source: {exc}")
                continue
            for node in ast.walk(tree):
                if isinstance(node, ast.Name) and node.id == "Any":
                    failures.append(f"{path.relative_to(ROOT)}:{node.lineno}: explicit Any name")
                elif isinstance(node, ast.Attribute) and node.attr == "Any":
                    failures.append(f"{path.relative_to(ROOT)}:{node.lineno}: qualified Any type")
                elif isinstance(node, ast.ImportFrom) and any(
                    alias.name == "Any" for alias in node.names
                ):
                    failures.append(f"{path.relative_to(ROOT)}:{node.lineno}: import of Any")
    return failures


def _workspace_package_source_roots() -> set[str]:
    workspace = tomllib.loads(CONFIG.read_text(encoding="utf-8"))
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
        roots.add((Path(member) / "src").as_posix())

    if errors:
        raise ValueError("\n".join(errors))
    return roots


def _basedpyright_include_roots() -> set[str]:
    project = tomllib.loads(CONFIG.read_text(encoding="utf-8"))
    include = project.get("tool", {}).get("basedpyright", {}).get("include")
    if not isinstance(include, list) or not all(isinstance(path, str) for path in include):
        raise ValueError("[tool.basedpyright].include must list package source roots")
    return {Path(path).as_posix().rstrip("/") for path in include}


def main() -> int:
    try:
        workspace_roots = _workspace_package_source_roots()
        checker_roots = _basedpyright_include_roots()
    except (OSError, KeyError, TypeError, tomllib.TOMLDecodeError, ValueError) as exc:
        print(f"package typing inventory error: {exc}", file=sys.stderr)
        return 1

    missing = sorted(workspace_roots - checker_roots)
    stale = sorted(checker_roots - workspace_roots)
    if missing or stale:
        if missing:
            print("Missing from BasedPyright include:", file=sys.stderr)
            for root in missing:
                print(f"  {root}", file=sys.stderr)
        if stale:
            print("BasedPyright include contains non-workspace roots:", file=sys.stderr)
            for root in stale:
                print(f"  {root}", file=sys.stderr)
        return 1

    any_uses = _explicit_any_uses()
    if any_uses:
        print("Explicit Any is disallowed in workspace Python code:", file=sys.stderr)
        print("\n".join(f"  {failure}" for failure in any_uses), file=sys.stderr)
        return 1

    print(f"BasedPyright package inventory: {len(workspace_roots)} workspace packages covered")
    print("Explicit Any ban: package code, examples, scripts, tests, and stubs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

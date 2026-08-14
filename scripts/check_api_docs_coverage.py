#!/usr/bin/env python3
"""Fail when a public ``hedron`` export disappears from the API coverage map."""

from __future__ import annotations

import ast
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INIT = ROOT / "packages/hedron/src/hedron/__init__.py"
COVERAGE = ROOT / "docs/api/COVERAGE.md"
CLI_SOURCE = ROOT / "packages/hedron/src/hedron/cli.py"
CLI_REFERENCE = ROOT / "docs/api/CLI.md"


def public_exports(source: str) -> set[str]:
    tree = ast.parse(source)
    assignments = [
        node
        for node in tree.body
        if isinstance(node, ast.Assign)
        and any(isinstance(target, ast.Name) and target.id == "__all__" for target in node.targets)
    ]
    if not assignments:
        raise ValueError("hedron.__all__ assignment not found")
    value = ast.literal_eval(assignments[-1].value)
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ValueError("hedron.__all__ must be a literal list of strings")
    return set(value)


def documented_symbols(markdown: str) -> set[str]:
    symbols: set[str] = set()
    for span in re.findall(r"`([^`\n]+)`", markdown):
        for token in re.split(r"\s*,\s*", span):
            token = token.strip()
            if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", token):
                symbols.add(token)
    return symbols


def cli_commands(source: str) -> set[str]:
    """Return literal top-level argparse commands registered on ``sub``."""
    tree = ast.parse(source)
    commands: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call) or not node.args:
            continue
        function = node.func
        if not (
            isinstance(function, ast.Attribute)
            and function.attr == "add_parser"
            and isinstance(function.value, ast.Name)
            and function.value.id == "sub"
        ):
            continue
        value = node.args[0]
        if isinstance(value, ast.Constant) and isinstance(value.value, str):
            commands.add(value.value)
    return commands


def documented_cli_commands(markdown: str) -> set[str]:
    """Read top-level command names from level-three CLI reference headings."""
    commands: set[str] = set()
    for heading in re.findall(r"^###\s+(.+)$", markdown, flags=re.MULTILINE):
        for span in re.findall(r"`([^`]+)`", heading):
            commands.add(span.split()[0])
    return commands


def main() -> int:
    exports = public_exports(INIT.read_text(encoding="utf-8"))
    documented = documented_symbols(COVERAGE.read_text(encoding="utf-8"))
    missing = sorted(exports - documented)
    if missing:
        raise SystemExit(
            "docs/api/COVERAGE.md is missing public exports:\n  " + "\n  ".join(missing)
        )
    commands = cli_commands(CLI_SOURCE.read_text(encoding="utf-8"))
    documented_commands = documented_cli_commands(CLI_REFERENCE.read_text(encoding="utf-8"))
    missing_commands = sorted(commands - documented_commands)
    if missing_commands:
        raise SystemExit(
            "docs/api/CLI.md is missing top-level commands:\n  " + "\n  ".join(missing_commands)
        )
    print(
        f"ok: all {len(exports)} hedron.__all__ exports and "
        f"{len(commands)} CLI commands appear in API docs"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

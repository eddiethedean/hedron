#!/usr/bin/env python3
"""Fail when public Edron, Hedron, charts, or CLI exports disappear from reference."""

from __future__ import annotations

import ast
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INIT = ROOT / "packages/hedron/src/hedron/__init__.py"
COVERAGE = ROOT / "docs/api/COVERAGE.md"
CLI_SOURCE = ROOT / "packages/hedron/src/hedron/cli/parser.py"
CLI_REFERENCE = ROOT / "docs/api/CLI.md"
CHARTS_INIT = ROOT / "packages/hedron-charts/src/hedron_charts/__init__.py"
CHARTS_REFERENCE = ROOT / "docs/api/CHART.md"
EDRON_INIT = ROOT / "packages/edron/src/edron/__init__.py"
EDRON_EXPORTS = ROOT / "docs/api/EDRON_EXPORTS.md"
EDRON_AUTODOC = ROOT / "docs/api/EDRON_AUTODOC.md"
EDRON_CONTRACTS = (
    ROOT / "docs/api/EDRON.md",
    ROOT / "docs/api/EDRON_REFERENCE.md",
    ROOT / "docs/api/EDRON_STATE_INTERACTION.md",
)
FLAGSHIP_CONTRACTS = (
    ROOT / "docs/api/HEDRON.md",
    ROOT / "docs/api/ROUTER.md",
    ROOT / "docs/api/ACTION.md",
    ROOT / "docs/api/INTERACTION.md",
    ROOT / "docs/api/PAGE.md",
    ROOT / "docs/api/CSRF_COMPOSITION.md",
    ROOT / "docs/api/JOBS.md",
    ROOT / "docs/api/FIELD.md",
)


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


def coverage_table_symbols(markdown: str) -> set[str]:
    """Read exports only from the first column of coverage-map table rows."""
    first_cells: list[str] = []
    for line in markdown.splitlines():
        if not line.startswith("|"):
            continue
        cells = line.split("|")
        if len(cells) >= 3 and "`" in cells[1]:
            first_cells.append(cells[1])
    return documented_symbols("\n".join(first_cells))


def require_contract_sections(path: Path) -> None:
    """Keep flagship hand-written references useful beyond symbol discovery."""
    headings = re.findall(r"^##\s+(.+)$", path.read_text(encoding="utf-8"), re.MULTILINE)
    normalized = [heading.casefold() for heading in headings]
    missing = [
        label
        for label in ("parameters", "returns", "errors")
        if not any(heading.startswith(label) for heading in normalized)
    ]
    if missing:
        raise SystemExit(
            f"{path.relative_to(ROOT)} is missing flagship contract sections: "
            + ", ".join(missing)
        )


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
    documented = coverage_table_symbols(COVERAGE.read_text(encoding="utf-8"))
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
    charts_exports = public_exports(CHARTS_INIT.read_text(encoding="utf-8"))
    charts_documented = documented_symbols(CHARTS_REFERENCE.read_text(encoding="utf-8"))
    missing_charts = sorted(charts_exports - charts_documented)
    if missing_charts:
        raise SystemExit(
            "docs/api/CHART.md is missing hedron_charts exports:\n  " + "\n  ".join(missing_charts)
        )
    edron_exports = public_exports(EDRON_INIT.read_text(encoding="utf-8"))
    edron_documented = documented_symbols(EDRON_EXPORTS.read_text(encoding="utf-8"))
    missing_edron = sorted(edron_exports - edron_documented)
    if missing_edron:
        raise SystemExit(
            "docs/api/EDRON_EXPORTS.md is missing Edron exports:\n  " + "\n  ".join(missing_edron)
        )
    if "::: edron" not in EDRON_AUTODOC.read_text(encoding="utf-8"):
        raise SystemExit("docs/api/EDRON_AUTODOC.md must render the public edron module")
    for contract in EDRON_CONTRACTS:
        text = contract.read_text(encoding="utf-8")
        if "app.native(" in text:
            raise SystemExit(
                f"{contract.relative_to(ROOT)} documents invalid app.native(...); "
                "use app.native_surface(...)"
            )
    for contract in FLAGSHIP_CONTRACTS:
        require_contract_sections(contract)
    print(
        f"ok: all {len(exports)} hedron.__all__ exports and "
        f"{len(edron_exports)} edron.__all__ exports and "
        f"{len(charts_exports)} hedron_charts exports and {len(commands)} CLI commands "
        "appear in API docs; flagship contract sections are present"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

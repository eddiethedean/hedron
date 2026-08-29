#!/usr/bin/env python3
"""Generate the built-in HTMX/Alpine component usage inventory.

The inventory intentionally measures source-level component ownership rather than
rendered HTML from a hand-picked example.  Historical releases are read from
their immutable tags; the current 1.0 row is read from the checkout so the
report describes the source being released.
"""

from __future__ import annotations

import argparse
import ast
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "implementation" / "HTMX_ALPINE_COMPONENT_COUNTS.md"
COMPONENT_ROOTS = (
    ROOT / "packages" / "hedron-core" / "src" / "hedron_core" / "builtins",
    ROOT / "packages" / "hedron" / "src" / "hedron" / "builtins",
)
GIT_ROOTS = (
    "packages/hedron-core/src/hedron_core/builtins/",
    "packages/hedron/src/hedron/builtins/",
)


@dataclass(frozen=True, slots=True)
class ComponentUsage:
    name: str
    source: str
    alpine: bool
    htmx: bool

    @property
    def lane(self) -> str:
        if self.alpine and self.htmx:
            return "both"
        if self.alpine:
            return "alpine"
        if self.htmx:
            return "htmx"
        return "neither"


def _is_component(node: ast.ClassDef) -> bool:
    for base in node.bases:
        if isinstance(base, ast.Name) and base.id == "Component":
            return True
        if (
            isinstance(base, ast.Subscript)
            and isinstance(base.value, ast.Name)
            and base.value.id == "Component"
        ):
            return True
    return False


class _UsageVisitor(ast.NodeVisitor):
    """Find emitted/typed engine references while ignoring prose docstrings."""

    def __init__(self) -> None:
        self.alpine = False
        self.htmx = False

    def visit_Name(self, node: ast.Name) -> None:
        if node.id in {"AlpineAttrs", "AlpineDirective", "AlpineExpression"}:
            self.alpine = True
        if node.id in {
            "HtmxAttrs",
            "HtmxLink",
            "Hx",
            "htmx_attrs",
            "hx_attr",
            "hx_attrs",
        }:
            self.htmx = True
        if node.id == "require_htmx_extension":
            self.htmx = True
        self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute) -> None:
        if node.attr in {"hx_attrs", "hx_attr"}:
            self.htmx = True
        self.generic_visit(node)

    def visit_arg(self, node: ast.arg) -> None:
        if isinstance(node.annotation, ast.Name) and node.annotation.id in {
            "AlpineAttrs",
            "HtmxAttrs",
            "Hx",
        }:
            self.alpine |= node.annotation.id == "AlpineAttrs"
            self.htmx |= node.annotation.id in {"HtmxAttrs", "Hx"}
        self.generic_visit(node)

    def visit_keyword(self, node: ast.keyword) -> None:
        if node.arg == "alpine":
            self.alpine = True
        if node.arg is not None and (node.arg == "htmx" or node.arg.startswith("hx_")):
            self.htmx = True
        self.generic_visit(node)

    def visit_Subscript(self, node: ast.Subscript) -> None:
        slice_node = node.slice
        if isinstance(slice_node, ast.Constant) and isinstance(slice_node.value, str):
            self.htmx |= slice_node.value.startswith("hx-")
        self.generic_visit(node)

    def visit_Dict(self, node: ast.Dict) -> None:
        for key in node.keys:
            if isinstance(key, ast.Constant) and isinstance(key.value, str):
                self.htmx |= key.value.startswith("hx-")
        self.generic_visit(node)

    def visit_JoinedStr(self, node: ast.JoinedStr) -> None:
        for value in node.values:
            if isinstance(value, ast.Constant) and isinstance(value.value, str):
                self.htmx |= value.value.startswith("hx-")
        self.generic_visit(node)


def _component_usage(source: str, path: str) -> tuple[ComponentUsage, ...]:
    tree = ast.parse(source, filename=path)
    rows: list[ComponentUsage] = []
    for node in tree.body:
        if not isinstance(node, ast.ClassDef) or not _is_component(node):
            continue
        visitor = _UsageVisitor()
        for child in node.body:
            visitor.visit(child)
        rows.append(ComponentUsage(node.name, path, visitor.alpine, visitor.htmx))
    return tuple(rows)


def _git_files(ref: str) -> tuple[str, ...]:
    result = subprocess.run(
        ["git", "ls-tree", "-r", "--name-only", ref, "--", *GIT_ROOTS],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return tuple(
        path
        for path in result.stdout.splitlines()
        if path.endswith(".py") and not path.endswith("/__init__.py")
    )


def _git_source(ref: str, path: str) -> str:
    result = subprocess.run(
        ["git", "show", f"{ref}:{path}"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout


def _working_tree_files() -> tuple[Path, ...]:
    return tuple(
        sorted(
            path
            for component_root in COMPONENT_ROOTS
            for path in component_root.rglob("*.py")
            if path.name != "__init__.py"
        )
    )


def _working_tree_usage() -> tuple[ComponentUsage, ...]:
    rows: list[ComponentUsage] = []
    for path in _working_tree_files():
        rows.extend(
            _component_usage(
                path.read_text(encoding="utf-8"),
                path.relative_to(ROOT).as_posix(),
            )
        )
    return tuple(rows)


def _ref_usage(ref: str) -> tuple[ComponentUsage, ...]:
    rows: list[ComponentUsage] = []
    for path in _git_files(ref):
        rows.extend(_component_usage(_git_source(ref, path), path))
    return tuple(rows)


def _counts(rows: tuple[ComponentUsage, ...]) -> dict[str, int]:
    return {
        "total": len(rows),
        "htmx": sum(row.htmx for row in rows),
        "alpine": sum(row.alpine for row in rows),
        "both": sum(row.alpine and row.htmx for row in rows),
        "either": sum(row.alpine or row.htmx for row in rows),
        "neither": sum(not row.alpine and not row.htmx for row in rows),
    }


def _names(rows: tuple[ComponentUsage, ...], lane: str) -> str:
    selected = sorted(row.name for row in rows if row.lane == lane)
    return ", ".join(f"`{name}`" for name in selected) or "None"


def render_report(releases: tuple[tuple[str, str, tuple[ComponentUsage, ...]], ...]) -> str:
    lines = [
        "# HTMX/Alpine component usage counts",
        "",
        "This report is generated by `scripts/generate_htmx_alpine_component_counts.py`.",
        "It counts built-in `Component` subclasses under `hedron-core` and `hedron`, based on",
        "typed Alpine lowering or emitted HTMX attributes in the component implementation.",
        "Project components, documentation examples, adapters, and specialist satellites are not",
        "included. A component in the `both` column is counted in both the HTMX and Alpine totals.",
        "",
        "## Summary",
        "",
        "| Release boundary | Source | Built-ins | HTMX | Alpine | Both | Either | Neither |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for label, source, rows in releases:
        counts = _counts(rows)
        lines.append(
            f"| {label} | `{source}` | {counts['total']} | {counts['htmx']} | "
            f"{counts['alpine']} | {counts['both']} | {counts['either']} | {counts['neither']} |"
        )
    lines.extend(
        [
            "",
            "## Component detail",
            "",
            "The lists below are mutually exclusive: `HTMX-only`, `Alpine-only`, `Both`, and",
            "`Neither` partition the built-in component catalog for each release boundary.",
            "",
        ]
    )
    for label, source, rows in releases:
        lines.extend(
            [
                f"### {label} (`{source}`)",
                "",
                f"- HTMX-only: {_names(rows, 'htmx')}",
                f"- Alpine-only: {_names(rows, 'alpine')}",
                f"- Both: {_names(rows, 'both')}",
                f"- Neither: {_names(rows, 'neither')}",
                "",
            ]
        )
    return "\n".join(lines)


def generate() -> str:
    releases = (
        ("0.66.2", "v0.66.2", _ref_usage("v0.66.2")),
        ("0.67.0", "v0.67.0", _ref_usage("v0.67.0")),
        ("1.0.0", "working tree", _working_tree_usage()),
    )
    return render_report(releases)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="verify the checked-in report instead of writing it",
    )
    args = parser.parse_args(argv)
    try:
        generated = generate()
    except (OSError, subprocess.CalledProcessError, SyntaxError) as exc:
        print(f"component count generation failed: {exc}", file=sys.stderr)
        return 2
    if args.check:
        current = REPORT.read_text(encoding="utf-8") if REPORT.exists() else ""
        if current != generated:
            print(f"{REPORT.relative_to(ROOT)} is stale; run this generator", file=sys.stderr)
            return 1
        print(f"ok: {REPORT.relative_to(ROOT)} is current")
        return 0
    REPORT.write_text(generated, encoding="utf-8")
    print(f"wrote {REPORT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

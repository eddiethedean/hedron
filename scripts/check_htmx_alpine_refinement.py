#!/usr/bin/env python3
"""Check the enforced seams of the HTMX/Alpine refinement."""

from __future__ import annotations

import ast
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
UI_PATHS = (
    ROOT / "packages/hedron-core/src/hedron_core/static/hedron-ui.mjs",
    ROOT / "packages/hedron/src/hedron/static/hedron-ui.mjs",
)
RAW_HTMX_ROOTS = (
    ROOT / "packages/hedron-core/src/hedron_core/builtins",
    ROOT / "packages/hedron-core/src/hedron_core/hosts.py",
    ROOT / "packages/hedron-core/src/hedron_core/sse_ext.py",
    ROOT / "packages/hedron/src/hedron/builtins",
    ROOT / "packages/hedron/src/hedron/handles.py",
    ROOT / "packages/hedron/src/hedron/routing/reverse.py",
)


class _RawHtmxWriterVisitor(ast.NodeVisitor):
    """Find literal HTMX writers while ignoring prose and allowlist sets."""

    def __init__(self) -> None:
        self.lines: list[int] = []

    def _record(self, node: ast.AST) -> None:
        self.lines.append(node.lineno)

    @staticmethod
    def _is_hx_key(node: ast.AST | None) -> bool:
        return (
            isinstance(node, ast.Constant)
            and isinstance(node.value, str)
            and node.value.lower().startswith("hx-")
        )

    def visit_Dict(self, node: ast.Dict) -> None:
        for key in node.keys:
            if self._is_hx_key(key):
                self._record(key)
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        for keyword in node.keywords:
            if keyword.arg is not None and keyword.arg.lower().startswith("hx_"):
                self._record(keyword)
        self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign) -> None:
        for target in node.targets:
            if isinstance(target, ast.Subscript) and self._is_hx_key(target.slice):
                self._record(target)
        self.generic_visit(node)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        target = node.target
        if isinstance(target, ast.Subscript) and self._is_hx_key(target.slice):
            self._record(target)
        self.generic_visit(node)


def main() -> int:
    errors: list[str] = []
    ui_sources = [path.read_text(encoding="utf-8") for path in UI_PATHS]
    if len(set(ui_sources)) != 1:
        errors.append("Hedron UI runtime copies must remain byte-identical")
    for path, source in zip(UI_PATHS, ui_sources, strict=True):
        if "htmx.ajax" in source:
            errors.append(f"{path.relative_to(ROOT)} must not start parallel HTMX requests")
        if "activeRequests" not in source or "finishRequest" not in source:
            errors.append(f"{path.relative_to(ROOT)} must use correlated request finalization")
    bridge_paths = (
        ROOT / "packages/hedron-core/src/hedron_core/static/hedron-htmx.mjs",
        ROOT / "packages/hedron/src/hedron/static/hedron-htmx.mjs",
    )
    bridge_sources = [path.read_text(encoding="utf-8") for path in bridge_paths]
    if len(set(bridge_sources)) != 1:
        errors.append("Hedron HTMX bridge copies must remain byte-identical")
    for path, source in zip(bridge_paths, bridge_sources, strict=True):
        if "htmx.ajax" in source:
            errors.append(f"{path.relative_to(ROOT)} must not start parallel HTMX requests")
        if "activeRequests" not in source or "finishRequest" not in source:
            errors.append(f"{path.relative_to(ROOT)} must use correlated request finalization")

    for root in RAW_HTMX_ROOTS:
        paths = (root,) if root.is_file() else sorted(root.rglob("*.py"))
        for path in paths:
            if path.name == "attrs.py":
                continue
            source = path.read_text(encoding="utf-8")
            visitor = _RawHtmxWriterVisitor()
            visitor.visit(ast.parse(source, filename=str(path)))
            if visitor.lines:
                errors.append(
                    f"{path.relative_to(ROOT)} emits raw hx-* writer(s) on line(s) "
                    f"{', '.join(str(line) for line in visitor.lines)}; use HtmxAttrs"
                )

    try:
        from hedron_core.htmx.attrs import HtmxAttrs, Hx

        if not issubclass(Hx, HtmxAttrs) or Hx().swap != "outerHTML":
            errors.append("Hx must remain an outerHTML-default compatibility wrapper")
    except ImportError as exc:
        errors.append(f"generic HTMX builder is not importable: {exc}")

    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print("ok: HTMX/Alpine refinement seams")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

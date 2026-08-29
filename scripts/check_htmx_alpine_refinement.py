#!/usr/bin/env python3
"""Check the enforced seams of the HTMX/Alpine refinement."""

from __future__ import annotations

import re
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
RAW_HTMX_ASSIGNMENT = re.compile(r"\[[\"']hx-[a-z0-9-]+[\"']\]\s*=")


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

    for root in RAW_HTMX_ROOTS:
        paths = (root,) if root.is_file() else sorted(root.rglob("*.py"))
        for path in paths:
            if path.name == "attrs.py":
                continue
            source = path.read_text(encoding="utf-8")
            if RAW_HTMX_ASSIGNMENT.search(source):
                errors.append(
                    f"{path.relative_to(ROOT)} emits raw hx-* assignment; use HtmxAttrs"
                )

    try:
        from hedron_core.htmx.attrs import HtmxAttrs, Hx

        if Hx is not HtmxAttrs:
            errors.append("Hx must remain a compatibility alias for HtmxAttrs")
    except ImportError as exc:
        errors.append(f"generic HTMX builder is not importable: {exc}")

    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print("ok: HTMX/Alpine refinement seams")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

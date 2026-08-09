#!/usr/bin/env python3
"""FACADE-023: verify Beginner/stable facade inventory is importable and deny-clean.

Parses the fenced ``text`` inventory under ``## Inventory (machine-checked)`` in
``docs/api/STABLE_FACADE.md``. Entries are ``module:Name`` or ``module:Class.method``.
"""

from __future__ import annotations

import ast
import importlib
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FACADE = ROOT / "docs" / "api" / "STABLE_FACADE.md"

DENY_SUBSTRINGS = (
    "experimental",
    "job_status_sse_response",
    "SseResponse",
    "StreamingComponentResponse",
    "DataTable",
    "DataEditor",
    "MatplotlibChart",
    "ModelDemo",
    "InferenceWorkflow",
)

INVENTORY_HEADING = "## Inventory (machine-checked)"
FENCE_RE = re.compile(r"```text\n(.*?)```", re.S)


def parse_inventory(text: str) -> list[str]:
    idx = text.find(INVENTORY_HEADING)
    if idx < 0:
        raise ValueError(f"missing heading {INVENTORY_HEADING!r} in {FACADE}")
    rest = text[idx:]
    match = FENCE_RE.search(rest)
    if not match:
        raise ValueError("missing ```text inventory fence after machine-checked heading")
    lines: list[str] = []
    for raw in match.group(1).splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        lines.append(line)
    return lines


def resolve_attr(module: object, dotted: str) -> object:
    obj: object = module
    for part in dotted.split("."):
        if not hasattr(obj, part):
            raise AttributeError(dotted)
        obj = getattr(obj, part)
    return obj


def main() -> int:
    errors: list[str] = []
    if not FACADE.is_file():
        print(f"missing facade inventory: {FACADE}", file=sys.stderr)
        return 1

    text = FACADE.read_text(encoding="utf-8")
    try:
        entries = parse_inventory(text)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    if len(entries) < 20:
        errors.append(f"inventory unexpectedly small: {len(entries)} entries")

    for entry in entries:
        lower = entry.lower()
        for needle in DENY_SUBSTRINGS:
            if needle.lower() in lower:
                errors.append(f"deny-list hit in inventory entry {entry!r}: {needle}")

        if ":" not in entry:
            errors.append(f"invalid inventory entry (want module:Name): {entry!r}")
            continue
        module_name, attr = entry.split(":", 1)
        if not module_name or not attr:
            errors.append(f"invalid inventory entry: {entry!r}")
            continue
        try:
            module = importlib.import_module(module_name)
            resolve_attr(module, attr)
        except Exception as exc:  # noqa: BLE001 — report any import/attr failure
            errors.append(f"{entry}: {type(exc).__name__}: {exc}")

    # Inventory fence must not be nested inside an excluded docs path check — just present.
    if "hedron.experimental" in text and "Deny list" not in text:
        errors.append("unexpected hedron.experimental outside deny guidance")

    # Sanity: parse as trivial AST of names for typos like spaces
    for entry in entries:
        _, attr = entry.split(":", 1)
        try:
            ast.parse(attr, mode="eval")
        except SyntaxError:
            errors.append(f"attr is not a dotted name: {entry!r}")

    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(f"ok: stable facade inventory ({len(entries)} entries)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

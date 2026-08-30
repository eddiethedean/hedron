#!/usr/bin/env python3
"""Execute and render the Basic use example for every generated component page."""

# Imports below intentionally follow the source-tree path setup.
# ruff: noqa: E402, I001

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
for source in (
    ROOT / "packages/hedron-core/src",
    ROOT / "packages/hedron/src",
    ROOT / "packages/hedron-data/src",
    ROOT / "packages/hedron-charts/src",
):
    sys.path.insert(0, str(source))

from hedron import RenderMode, render
from hedron_core.diagnostics import DiagnosticSeverity
from scripts.generate_component_docs import COMPONENTS, resolve_spec

_BASIC = re.compile(r"^## Basic use\s+```python\n(?P<code>.*?\n)```", re.MULTILINE | re.DOTALL)


def _basic_code(path: Path) -> str:
    match = _BASIC.search(path.read_text(encoding="utf-8"))
    if match is None:
        raise AssertionError(f"{path.relative_to(ROOT)} has no Basic use Python block")
    return match.group("code")


def main() -> int:
    failures: list[str] = []
    skipped: list[str] = []
    for manifest_spec in COMPONENTS:
        spec = resolve_spec(manifest_spec)
        path = ROOT / "docs" / "components" / f"{spec.slug}.md"
        namespace: dict[str, object] = {"__name__": "__docs_component_example__"}
        try:
            exec(compile(_basic_code(path), str(path), "exec"), namespace, namespace)
        except ImportError as exc:
            if "[" in spec.package:
                skipped.append(f"{spec.name}: optional dependency unavailable ({exc})")
                continue
            failures.append(f"{spec.name}: import failed: {exc}")
            continue
        except Exception as exc:  # noqa: BLE001  # docs examples must report all failures
            failures.append(f"{spec.name}: example failed: {type(exc).__name__}: {exc}")
            continue

        if not spec.renderable:
            continue
        component = namespace.get("component")
        if component is None:
            failures.append(f"{spec.name}: Basic use example does not define component")
            continue
        try:
            mode = RenderMode.PAGE if spec.name == "Page" else RenderMode.FRAGMENT
            result = render(component, mode=mode)
        except Exception as exc:  # noqa: BLE001  # docs examples must report all failures
            failures.append(f"{spec.name}: render failed: {type(exc).__name__}: {exc}")
            continue
        errors = [
            diagnostic
            for diagnostic in result.diagnostics
            if diagnostic.severity is DiagnosticSeverity.ERROR
        ]
        if not result.html:
            failures.append(f"{spec.name}: render returned empty HTML")
        elif errors:
            details = ", ".join(f"{item.code}: {item.message}" for item in errors)
            failures.append(f"{spec.name}: render diagnostics: {details}")

    for item in skipped:
        print(f"SKIP {item}")
    for item in failures:
        print(f"FAIL {item}")
    print(f"checked {len(COMPONENTS)} generated component examples")
    print(f"skipped {len(skipped)} optional examples")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())

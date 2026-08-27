"""fastapi_workbench must not import Hedron packages."""

from __future__ import annotations

import ast
from pathlib import Path

FORBIDDEN = frozenset({"hedron", "hedron_core"})


def test_no_hedron_imports_in_fastapi_workbench() -> None:
    root = Path(__file__).resolve().parents[2] / "packages" / "fastapi-workbench" / "src"
    offenders: list[str] = []
    for path in root.rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    top = alias.name.split(".", 1)[0]
                    if top in FORBIDDEN:
                        offenders.append(f"{path}: import {alias.name}")
            elif isinstance(node, ast.ImportFrom) and node.module:
                top = node.module.split(".", 1)[0]
                if top in FORBIDDEN:
                    offenders.append(f"{path}: from {node.module}")
    assert not offenders, "\n".join(offenders)

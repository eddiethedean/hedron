"""ADP-005: Explorer does not hard-require the FastAPI flagship package."""

from __future__ import annotations

import ast
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_explorer_pyproject_depends_on_core_not_hedron() -> None:
    data = tomllib.loads(
        (ROOT / "packages" / "hedron-explorer" / "pyproject.toml").read_text(encoding="utf-8")
    )
    deps = " ".join(data["project"].get("dependencies", [])).lower()
    assert "hedron-core" in deps
    assert "hedron==" not in deps
    assert "hedron>=" not in deps


def test_flask_django_do_not_depend_on_fastapi_or_explorer() -> None:
    for name in ("hedron-flask", "hedron-django"):
        data = tomllib.loads(
            (ROOT / "packages" / name / "pyproject.toml").read_text(encoding="utf-8")
        )
        deps = " ".join(data["project"].get("dependencies", [])).lower()
        assert "fastapi" not in deps
        assert "hedron-explorer" not in deps
        assert "hedron==" not in deps


def test_explorer_source_avoids_hard_hedron_imports() -> None:
    src = ROOT / "packages" / "hedron-explorer" / "src" / "hedron_explorer"
    hard: list[str] = []
    for path in src.rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name == "hedron" or alias.name.startswith("hedron."):
                        hard.append(f"{path.name}: import {alias.name}")
            elif (
                isinstance(node, ast.ImportFrom)
                and node.module
                and (node.module == "hedron" or node.module.startswith("hedron."))
            ):
                hard.append(f"{path.name}: from {node.module}")
    assert hard == []

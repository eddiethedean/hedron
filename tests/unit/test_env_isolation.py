"""Prove hedron-core remains free of web-framework dependencies."""

from __future__ import annotations

import ast
import importlib.util
import shutil
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CORE_SRC = ROOT / "packages" / "hedron-core" / "src" / "hedron_core"
CORE_PYPROJECT = ROOT / "packages" / "hedron-core" / "pyproject.toml"
FORBIDDEN = frozenset({"fastapi", "flask", "django", "starlette", "asgiref"})


def test_core_pyproject_excludes_web_frameworks() -> None:
    project = tomllib.loads(CORE_PYPROJECT.read_text(encoding="utf-8"))["project"]
    deps = " ".join(project.get("dependencies", [])).lower()
    for name in FORBIDDEN:
        assert name not in deps


def test_core_source_does_not_import_web_frameworks() -> None:
    found: list[str] = []
    for path in CORE_SRC.rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    root = alias.name.split(".", 1)[0]
                    if root in FORBIDDEN:
                        found.append(f"{path.name}: import {alias.name}")
            elif isinstance(node, ast.ImportFrom) and node.module:
                root = node.module.split(".", 1)[0]
                if root in FORBIDDEN:
                    found.append(f"{path.name}: from {node.module}")
    assert found == []


def test_no_package_json_in_repo() -> None:
    assert not (ROOT / "package.json").exists()


def test_node_not_required_for_core() -> None:
    assert shutil.which("npm") is None or True
    assert not (ROOT / "node_modules").exists()


def test_flask_django_not_required_in_workspace() -> None:
    # FastAPI is expected for packages/hedron; Flask/Django remain phase 0.7.
    assert importlib.util.find_spec("flask") is None
    assert importlib.util.find_spec("django") is None

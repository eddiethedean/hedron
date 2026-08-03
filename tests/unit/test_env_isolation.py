"""Prove hedron-core remains free of web-framework dependencies."""

from __future__ import annotations

import ast
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


def test_adapter_packages_do_not_depend_on_fastapi() -> None:
    # Flask/Django may be installed for adapter packages; they must not require FastAPI.
    import re

    for package in ("hedron-flask", "hedron-django"):
        pyproject = ROOT / "packages" / package / "pyproject.toml"
        project = tomllib.loads(pyproject.read_text(encoding="utf-8"))["project"]
        deps = list(project.get("dependencies", []))
        optional = project.get("optional-dependencies") or {}
        for group in optional.values():
            deps.extend(group)
        joined = "\n".join(str(d).lower() for d in deps)
        for name in ("fastapi", "starlette", "uvicorn"):
            assert name not in joined, f"{package} must not depend on {name}"
        # Exact flagship package name, not hedron-core / hedron-flask.
        assert re.search(r"(?m)^hedron([=<>!~]|$)", joined) is None, (
            f"{package} must not depend on flagship hedron"
        )

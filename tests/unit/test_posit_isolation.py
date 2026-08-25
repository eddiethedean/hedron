"""hedron / hedron_core / fastapi_workbench must not import hedron_posit."""

from __future__ import annotations

import ast
import sys
import tomllib
from pathlib import Path

import pytest

import fastapi_workbench
import hedron
import hedron_core

ROOT = Path(__file__).resolve().parents[2]


def test_flagship_does_not_import_posit() -> None:
    assert "hedron_posit" not in getattr(hedron, "__dict__", {})
    assert "hedron_posit" not in getattr(hedron_core, "__dict__", {})
    assert "hedron_posit" not in getattr(fastapi_workbench, "__dict__", {})


def test_posit_does_not_import_workbench() -> None:
    import hedron_posit

    assert "hedron_workbench" not in sys.modules or "hedron_workbench" not in getattr(
        hedron_posit, "__dict__", {}
    )
    assert "hedron_workbench" not in getattr(hedron_posit, "__dict__", {})


def test_posit_does_not_depend_on_fastapi_workbench() -> None:
    package = ROOT / "packages" / "hedron-posit"
    project = tomllib.loads((package / "pyproject.toml").read_text(encoding="utf-8"))["project"]
    assert not any(
        str(dependency).startswith("fastapi-workbench") for dependency in project["dependencies"]
    )

    for source in (package / "src" / "hedron_posit").rglob("*.py"):
        tree = ast.parse(source.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                assert all(not alias.name.startswith("fastapi_workbench") for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                assert not (node.module or "").startswith("fastapi_workbench")


def test_import_does_not_wrap(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("RS_SERVER_URL", "https://wb.example/s/x/")
    monkeypatch.delenv("HEDRON_ROOT_PATH", raising=False)
    import importlib

    import hedron_posit

    importlib.reload(hedron_posit)
    assert "HEDRON_ROOT_PATH" not in __import__("os").environ
    assert callable(hedron_posit.workbenchify)
    assert hedron_posit.HedronPosit.__name__ == "HedronPosit"

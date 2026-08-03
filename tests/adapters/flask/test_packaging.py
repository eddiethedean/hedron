"""Packaging checks for hedron-flask."""

from __future__ import annotations

import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PYPROJECT = ROOT / "packages" / "hedron-flask" / "pyproject.toml"


def _deps_text() -> str:
    project = tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))["project"]
    parts: list[str] = list(project.get("dependencies", []))
    for group in (project.get("optional-dependencies") or {}).values():
        parts.extend(group)
    return " ".join(parts).lower()


def test_pyproject_has_no_fastapi() -> None:
    deps = _deps_text()
    for name in ("fastapi", "starlette", "uvicorn"):
        assert name not in deps


def test_pyproject_declares_flask_and_core() -> None:
    deps = _deps_text()
    assert "flask" in deps
    assert "hedron-core" in deps
    assert "werkzeug" in deps

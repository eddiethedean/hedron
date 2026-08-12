"""Upgrade fixtures: hedron-workbench 0.29.0 → 0.30.0 dependency inversion."""

from __future__ import annotations

import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_hedron_workbench_declares_fastapi_workbench_dependency() -> None:
    pyproject = ROOT / "packages" / "hedron-workbench" / "pyproject.toml"
    data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
    deps = data["project"]["dependencies"]
    assert any("fastapi-workbench>=1.0.0,<2.0" in dep for dep in deps)


def test_coordinated_train_is_030() -> None:
    pyproject = ROOT / "packages" / "hedron-workbench" / "pyproject.toml"
    data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
    assert data["project"]["version"] == "0.30.0"


def test_fastapi_workbench_independent_version() -> None:
    pyproject = ROOT / "packages" / "fastapi-workbench" / "pyproject.toml"
    data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
    assert data["project"]["version"] == "1.0.0"

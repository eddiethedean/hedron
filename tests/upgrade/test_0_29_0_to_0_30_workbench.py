"""Upgrade fixtures: hedron-workbench 0.29.0 → 0.30.0 dependency inversion.

After 0.33, ``hedron-workbench`` depends on ``hedron-posit``, which owns the
``fastapi-workbench`` dependency (one-way graph).
"""

from __future__ import annotations

import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_hedron_posit_declares_fastapi_workbench_dependency() -> None:
    pyproject = ROOT / "packages" / "hedron-posit" / "pyproject.toml"
    data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
    deps = data["project"]["dependencies"]
    assert any("fastapi-workbench>=1.0.0,<2.0" in dep for dep in deps)


def test_workbench_depends_on_posit() -> None:
    pyproject = ROOT / "packages" / "hedron-workbench" / "pyproject.toml"
    data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
    deps = data["project"]["dependencies"]
    assert any(dep.startswith("hedron-posit") for dep in deps)


def test_coordinated_train_tracks_living_tip() -> None:
    """0.30 introduced the fastapi-workbench split; tip stays coordinated afterward."""
    release = tomllib.loads((ROOT / "docs" / "release.toml").read_text(encoding="utf-8"))["release"]
    pyproject = ROOT / "packages" / "hedron-workbench" / "pyproject.toml"
    data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
    assert data["project"]["version"] == release["development_version"]


def test_fastapi_workbench_independent_version() -> None:
    pyproject = ROOT / "packages" / "fastapi-workbench" / "pyproject.toml"
    data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
    assert data["project"]["version"] == "1.0.1"

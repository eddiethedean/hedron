"""Upgrade fixtures: hedron-posit extraction / workbench thin compat (0.32 → 0.33)."""

from __future__ import annotations

import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_hedron_posit_package_exists() -> None:
    pyproject = ROOT / "packages" / "hedron-posit" / "pyproject.toml"
    data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
    assert data["project"]["name"] == "hedron-posit"
    deps = data["project"]["dependencies"]
    assert any(dep.startswith("fastapi-workbench") for dep in deps)
    assert any(dep.startswith("hedron") for dep in deps)
    assert not any("hedron-workbench" in dep for dep in deps)


def test_workbench_depends_on_posit_only() -> None:
    pyproject = ROOT / "packages" / "hedron-workbench" / "pyproject.toml"
    data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
    deps = data["project"]["dependencies"]
    assert any(dep.startswith("hedron-posit") for dep in deps)
    assert not any(dep.startswith("fastapi-workbench") for dep in deps)
    assert not any(
        dep.startswith("hedron>=") or dep.startswith("hedron<") or dep == "hedron" for dep in deps
    )


def test_hedron_extras_declare_posit_and_workbench() -> None:
    pyproject = ROOT / "packages" / "hedron" / "pyproject.toml"
    data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
    extras = data["project"]["optional-dependencies"]
    assert any("hedron-posit" in dep for dep in extras["posit"])
    assert any("hedron-workbench" in dep for dep in extras["workbench"])


def test_workbench_subclass_import_path() -> None:
    from hedron_posit import HedronPosit
    from hedron_workbench import HedronWorkbench

    assert issubclass(HedronWorkbench, HedronPosit)

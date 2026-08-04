"""Packaging metadata checks for the 0.8 packaging gate."""

from __future__ import annotations

import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_all_packages_declare_license_and_version() -> None:
    for pyproject in sorted((ROOT / "packages").glob("*/pyproject.toml")):
        project = tomllib.loads(pyproject.read_text(encoding="utf-8"))["project"]
        assert project["version"] == "0.8.0", pyproject
        assert "license" in project or "license-files" in project, pyproject.name
        assert (pyproject.parent / "LICENSE").is_file()


def test_django_and_flask_wheels_metadata_isolation() -> None:
    for name in ("hedron-flask", "hedron-django"):
        project = tomllib.loads(
            (ROOT / "packages" / name / "pyproject.toml").read_text(encoding="utf-8")
        )["project"]
        deps = " ".join(project.get("dependencies", [])).lower()
        assert "fastapi" not in deps
        assert "starlette" not in deps
        assert "hedron-core" in deps


def test_evidence_scripts_exist() -> None:
    for script in (
        "generate_sbom.py",
        "license_inventory.py",
        "asset_audit.py",
        "dep_audit.py",
        "build_evidence_bundle.py",
        "check_stability_inventory.py",
    ):
        assert (ROOT / "scripts" / script).is_file()

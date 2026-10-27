"""Python 3.11 support-policy and stdlib transition checks."""

from __future__ import annotations

import tomllib
from enum import StrEnum
from pathlib import Path

from packaging.specifiers import SpecifierSet
from scripts.check_python_311 import check
from scripts.check_release_gate import evidence_manifest_for

from hedron_core import compat

ROOT = Path(__file__).resolve().parents[2]


def test_all_workspace_metadata_matches_the_311_baseline() -> None:
    assert check() == []
    for pyproject in sorted((ROOT / "packages").glob("*/pyproject.toml")):
        project = tomllib.loads(pyproject.read_text(encoding="utf-8"))["project"]
        requires = SpecifierSet(project["requires-python"])
        assert not requires.contains("3.10"), project["name"]
        assert requires.contains("3.11"), project["name"]


def test_stdlib_compatibility_paths_reexport_native_objects() -> None:
    import tomllib as stdlib_tomllib

    assert compat.StrEnum is StrEnum
    assert compat.tomllib is stdlib_tomllib

    class State(StrEnum):
        READY = "ready"

    assert State.READY == "ready"
    assert str(State.READY) == "ready"
    assert compat.tomllib.loads("[phase]\nvalue = 12\n") == {"phase": {"value": 12}}


def test_release_tooling_selects_the_phase_12_packet() -> None:
    expected = ROOT / "docs" / "acceptance" / "release-gate-1.2.toml"
    assert evidence_manifest_for("1.2.0") == expected
    manifest = tomllib.loads(expected.read_text(encoding="utf-8"))
    assert manifest["python_requires"] == ">=3.11,<3.15"
    assert manifest["python_matrix"] == ["3.11", "3.12", "3.13", "3.14"]


def test_migration_analyzer_keeps_310_source_grammar_without_runtime_support() -> None:
    cli = (ROOT / "packages" / "hedron" / "src" / "hedron" / "migrate" / "cli.py").read_text(
        encoding="utf-8"
    )
    assert 'choices=("3.10", "3.11", "3.12", "3.13", "3.14")' in cli
    metadata = tomllib.loads(
        (ROOT / "packages" / "hedron" / "pyproject.toml").read_text(encoding="utf-8")
    )["project"]
    assert metadata["requires-python"] == ">=3.11,<3.15"

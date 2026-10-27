"""The installed-app rehearsal keeps its candidate pin and sources explicit."""

from __future__ import annotations

import tomllib

import pytest

from scripts import rehearse_python_311_upgrade_rollback as upgrade


def test_candidate_project_pins_candidate_wheels_and_next_minor_train(tmp_path) -> None:
    source = (
        '[project]\nname = "upgrade-fixture"\n'
        'requires-python = ">=3.10,<3.15"\n'
        'dependencies = ["hedron>=1.1.3,<1.2"]\n'
        '[build-system]\nrequires = ["hatchling"]\n'
        'build-backend = "hatchling.build"\n'
    )
    hedron = tmp_path / "hedron-1.2.0-py3-none-any.whl"
    core = tmp_path / "hedron_core-1.2.0-py3-none-any.whl"

    updated = upgrade.candidate_project_text(
        source,
        predecessor_version="1.1.3",
        candidate_version="1.2.0",
        hedron_wheel=hedron,
        core_wheel=core,
    )
    parsed = tomllib.loads(updated)

    assert parsed["project"]["requires-python"] == ">=3.11,<3.15"
    assert "hedron>=1.2.0,<1.3" in parsed["project"]["dependencies"]
    assert parsed["tool"]["uv"]["sources"] == {
        "hedron": {"path": str(hedron)},
        "hedron-core": {"path": str(core)},
    }


def test_candidate_project_rejects_ambiguous_existing_uv_sources(tmp_path) -> None:
    source = (
        '[project]\nrequires-python = ">=3.10,<3.15"\n'
        'dependencies = ["hedron>=1.1.3,<1.2"]\n'
        '[tool.uv.sources]\nother = { path = "../other" }\n'
    )

    with pytest.raises(ValueError, match=r"already defines \[tool.uv.sources\]"):
        upgrade.candidate_project_text(
            source,
            predecessor_version="1.1.3",
            candidate_version="1.2.0",
            hedron_wheel=tmp_path / "hedron.whl",
            core_wheel=tmp_path / "hedron_core.whl",
        )

"""Validation for explicitly loaded UI-testing package contributions."""

from __future__ import annotations

import importlib
from pathlib import Path
from types import SimpleNamespace

import pytest

from hedron.testing.browser_scenario import (
    UITestingContribution,
    validate_ui_testing_contribution,
)
from hedron.testing.pytest_plugin import _load_ui_contributions


def test_contribution_metadata_is_bounded_and_version_checked() -> None:
    contribution = UITestingContribution(
        package_id="hedron-sample-kit",
        package_version="0.2.6",
        hedron_version_range=">=1.2,<2",
        capabilities=("sample_component_app",),
        fixture_resources=("sample_kit_app_factory",),
    )

    validated = validate_ui_testing_contribution(contribution, hedron_version="1.2.0")

    assert validated.to_metadata() == {
        "schema_version": 1,
        "package_id": "hedron-sample-kit",
        "package_version": "0.2.6",
        "hedron_version_range": ">=1.2,<2",
        "capabilities": ["sample_component_app"],
        "fixture_resources": ["sample_kit_app_factory"],
    }
    with pytest.raises(ValueError, match="does not support"):
        validated.validate_for("2.0.0")


def test_json_shaped_contribution_metadata_is_validated() -> None:
    raw: dict[str, object] = {
        "schema_version": 1,
        "package_id": "hedron-sample-kit",
        "package_version": "0.2.6",
        "hedron_version_range": ">=1.2,<2",
        "capabilities": ["sample_component_app"],
        "fixture_resources": ["sample_kit_app_factory"],
    }

    validated = validate_ui_testing_contribution(raw, hedron_version="1.2.0")

    assert validated.to_metadata() == raw


@pytest.mark.parametrize(
    "mutation",
    [
        {"schema_version": True},
        {"package_id": "unknown", "unexpected": "field"},
        {"capabilities": ["duplicate", "duplicate"]},
        {"fixture_resources": "sample_kit_app_factory"},
    ],
)
def test_json_shaped_contribution_rejects_malformed_metadata(
    mutation: dict[str, object],
) -> None:
    raw: dict[str, object] = {
        "schema_version": 1,
        "package_id": "hedron-sample-kit",
        "package_version": "0.2.6",
        "hedron_version_range": ">=1.2,<2",
        "capabilities": ["sample_component_app"],
        "fixture_resources": ["sample_kit_app_factory"],
    }
    raw.update(mutation)

    with pytest.raises(ValueError):
        validate_ui_testing_contribution(raw, hedron_version="1.2.0")


@pytest.mark.parametrize(
    "kwargs",
    [
        {"schema_version": 2},
        {"package_id": "bad id"},
        {"package_version": "not-a-version"},
        {"hedron_version_range": "not a range"},
        {"capabilities": ("duplicate", "duplicate")},
        {"fixture_resources": ("invalid-name",)},
    ],
)
def test_contribution_rejects_invalid_metadata(kwargs: dict[str, object]) -> None:
    values: dict[str, object] = {
        "package_id": "hedron-sample-kit",
        "package_version": "0.2.6",
        "hedron_version_range": ">=1.2,<2",
        "capabilities": ("sample_component_app",),
        "fixture_resources": ("sample_kit_app_factory",),
    }
    values.update(kwargs)

    with pytest.raises(ValueError):
        _ = UITestingContribution(**values)  # pyright: ignore[reportArgumentType]


def test_dynamically_requested_fixture_loads_its_explicit_contribution(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    package = tmp_path / "dynamic_contribution"
    package.mkdir()
    (package / "__init__.py").write_text(
        "from hedron.testing.browser_scenario import UITestingContribution\n"
        "CONTRIBUTION = UITestingContribution(\n"
        " package_id='dynamic-probe', package_version='1.0.0',\n"
        " hedron_version_range='>=1.2,<2', capabilities=('probe',),\n"
        " fixture_resources=('dynamic_fixture',))\n",
        encoding="utf-8",
    )
    monkeypatch.syspath_prepend(str(tmp_path))
    importlib.invalidate_caches()
    marker = SimpleNamespace(
        args=("dynamic_contribution:CONTRIBUTION",),
        kwargs={},
    )
    item = SimpleNamespace(
        nodeid="test_dynamic",
        fixturenames=["dynamic_fixture"],
        iter_markers=lambda name: iter((marker,)) if name == "hedron_ui_contribution" else iter(()),
    )

    contributions = _load_ui_contributions(item)  # type: ignore[arg-type]

    assert len(contributions) == 1
    assert contributions[0].package_id == "dynamic-probe"
    sys_module = importlib.import_module("dynamic_contribution")
    assert contributions[0] is sys_module.CONTRIBUTION

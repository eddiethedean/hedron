"""AUTHOR-040 public authoring and scaffold contracts."""

from __future__ import annotations

from pathlib import Path

import pytest

from hedron.cli import main
from hedron_core import ElementFieldOwnership, get_registry
from hedron_core.diagnostics import HedronError
from hedron_core.plugins import PluginContext, PluginMeta
from hedron_core.registry import register_element_definition, reset_registry_for_tests
from hedron_elements import (
    AUTHOR_SURFACES,
    packaging_checklist,
    validate_element_author_meta,
)


def _author_meta() -> dict[str, object]:
    return {
        "tag_name": "ext-author-test",
        "abi_version": 1,
        "module_asset_id": "test:module",
        "logical_id": "test:element",
        "events": (),
        "lifecycle": {},
        "fallback": {},
        "a11y_contract": {},
        "attributes": (),
    }


def test_author_metadata_validation_and_checklist() -> None:
    meta = _author_meta()
    assert validate_element_author_meta(meta) == meta
    assert AUTHOR_SURFACES == (
        "element_metadata",
        "events",
        "lifecycle",
        "fallback",
        "assets",
        "a11y",
        "diagnostics",
    )
    with pytest.raises(HedronError) as exc:
        validate_element_author_meta({"tag_name": "ext-incomplete"})
    assert exc.value.diagnostic.code.startswith("HED-ELEMENT-AUTHOR-")
    checklist = "\n".join(packaging_checklist())
    assert "PluginContext" in checklist
    assert "no private registry imports" in checklist


def test_cli_scaffolds_element_with_public_plugin_api(tmp_path: Path) -> None:
    destination = tmp_path / "demo-probe"
    with pytest.raises(SystemExit) as exc:
        main(["new", "element", "demo-probe", "--path", str(destination)])
    assert exc.value.code == 0
    expected = (
        "pyproject.toml",
        "src/demo_probe/plugin.py",
        "src/demo_probe/static/demo-probe.mjs",
        "src/demo_probe/static/demo-probe.css",
        "tests/test_element.py",
        "examples/README.md",
    )
    assert all((destination / relative).is_file() for relative in expected)
    project = (destination / "pyproject.toml").read_text(encoding="utf-8")
    assert "hedron-core>=0.51.0,<0.52" in project
    assert "hedron-elements>=0.51.0,<0.52" in project
    plugin = (destination / "src/demo_probe/plugin.py").read_text(encoding="utf-8")
    assert "PLUGIN_META = _META" in plugin
    assert "ctx.register_element_definition" in plugin
    assert "from hedron_core.registry import register_element" not in plugin


def test_plugin_context_defaults_third_party_but_registry_defaults_first_party() -> None:
    reset_registry_for_tests()
    ctx = PluginContext(
        PluginMeta(
            name="author_test",
            version="0.1.0",
            distribution="author-test",
            hedron_version=">=0.40,<0.41",
        )
    )
    ctx.register_element_definition(
        logical_id="author-test:probe",
        tag_name="ext-author-test",
        abi_version=1,
        module_asset_id="author-test:probe.mjs",
    )
    registered = get_registry().get_element_definition("author-test:probe")
    assert registered is not None
    assert registered.first_party is False

    with pytest.raises(HedronError) as exc:
        register_element_definition(
            logical_id="author-test:first-party",
            tag_name="ext-first-party",
            abi_version=1,
            module_asset_id="author-test:first-party.mjs",
        )
    assert exc.value.diagnostic.code == "HED-ELEMENT-0003"


def test_state_ownership_is_validated_before_idempotent_registration() -> None:
    reset_registry_for_tests()
    invalid = ElementFieldOwnership(name="token", mode="local")
    with pytest.raises(HedronError) as exc:
        register_element_definition(
            logical_id="hedron:test",
            tag_name="hedron-test",
            abi_version=1,
            module_asset_id="hedron:test.mjs",
            state_ownership=(invalid,),
        )
    assert exc.value.diagnostic.code.startswith("HED-ELEMENT-STATE-")
    assert get_registry().get_element_definition("hedron:test") is None

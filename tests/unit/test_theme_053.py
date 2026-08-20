"""THEME-053 evidence."""

from __future__ import annotations

import tomllib
from pathlib import Path
from types import SimpleNamespace

from hedron_core import PRIVATE_SELECTORS_SUPPORTED, default_theme, run_visual_conformance
from hedron_core.registry import register_element_definition, reset_registry_for_tests


def test_theme_053_packet_bound() -> None:
    gate = tomllib.loads(Path("docs/acceptance/release-gate-0.53.toml").read_text(encoding="utf-8"))
    rows = {row["id"]: row for row in gate["evidence"]}
    assert rows["THEME-053"]["state"] == "Verified"
    assert Path("docs/rfcs/RFC-0080-APPLICATION-DX-CONTRACTS.md").is_file()


def test_run_visual_conformance_ok_for_default_theme() -> None:
    reset_registry_for_tests()
    assert PRIVATE_SELECTORS_SUPPORTED is False
    assert run_visual_conformance(default_theme()) == []
    assert run_visual_conformance(None) == []


def test_run_visual_conformance_reports_missing_token_sets() -> None:
    reset_registry_for_tests()
    incomplete = SimpleNamespace(tokens={"color.bg": "#fff"})
    diagnostics = run_visual_conformance(incomplete)
    codes = {item.code for item in diagnostics}
    assert "HED-THEME-0002" in codes
    missing_sets = {
        item.context.get("set") for item in diagnostics if item.code == "HED-THEME-0002"
    }
    assert "accessibility" in missing_sets
    assert "forced-colors" in missing_sets
    assert "print-safe" in missing_sets
    assert any("color.fg" in item.explanation for item in diagnostics)


def test_run_visual_conformance_validates_element_style_contract() -> None:
    reset_registry_for_tests()
    register_element_definition(
        logical_id="demo.bad",
        tag_name="hedron-demo-bad",
        abi_version=1,
        module_asset_id="demo.module",
        parts=("label",),
        slots={"default": "content"},
        tokens=("color.fg",),
        style_contract={"parts": "missing-part"},
    )
    register_element_definition(
        logical_id="demo.good",
        tag_name="hedron-demo-good",
        abi_version=1,
        module_asset_id="demo.module",
        parts=("label",),
        slots={"default": "content"},
        tokens=("color.fg",),
        style_contract={"parts": "label", "slots": "default", "tokens": "color.fg"},
    )
    diagnostics = run_visual_conformance(
        default_theme(),
        element_ids=("demo.bad", "demo.good", "demo.missing"),
    )
    codes_by_component: dict[str, set[str]] = {}
    for item in diagnostics:
        if item.component_id:
            codes_by_component.setdefault(item.component_id, set()).add(item.code)
    assert "HED-THEME-0005" in codes_by_component["demo.bad"]
    assert any(
        "Private selectors are not supported" in item.remediation
        for item in diagnostics
        if item.component_id == "demo.bad"
    )
    assert "HED-THEME-0006" in codes_by_component["demo.missing"]
    assert "HED-THEME-0005" not in codes_by_component.get("demo.good", set())

"""Required phase 0.63 theme authority and evidence contracts."""

from __future__ import annotations

import json
from pathlib import Path

from hedron_core import (
    Theme,
    build_state_matrix,
    component_contract_manifest,
    default_theme,
    element_metadata_manifest,
    emit_theme_css,
    export_theme,
    inspect_theme_css,
    theme_contract_report,
)


def test_custom_theme_controls_legacy_stylesheet_consumers() -> None:
    theme = default_theme().extend(
        "custom",
        tokens={"color.accent": "#9b2c8c", "color.focus": "#9b2c8c"},
        shape={"radius": "0.2rem"},
        elevation={"raised": "none"},
    )

    css = emit_theme_css(theme)

    assert "--hedron-color-accent: #9b2c8c;" in css
    assert "--hedron-color-link: #9b2c8c;" in css
    assert "--hedron-color-link-hover:" in css
    assert "--hedron-color-link-active:" in css
    assert "--hedron-color-link-visited:" in css
    assert "--hedron-color-selection-bg: #9b2c8c;" in css
    assert "--hedron-default-accent: var(--hedron-color-accent, #2563eb);" in css
    assert "--hedron-default-radius: var(--hedron-shape-radius, 0.2rem);" in css
    assert "--hedron-default-shadow: var(--hedron-elevation-raised, none);" in css


def test_component_manifest_and_matrix_are_registry_derived() -> None:
    manifest = component_contract_manifest()
    matrix = build_state_matrix(components=("Brand",), viewports=("390",), modes=("light",))

    assert manifest["schema"] == "hedron.component-theme-manifest/1"
    brand = next(item for item in manifest["components"] if item["logical_id"] == "Brand")
    assert brand["parts"] == ["mark", "copy", "name", "subtitle"]
    assert matrix.to_dict()["schema"] == "hedron.component-state-matrix/1"
    assert matrix.to_dict()["count"] == 1
    assert matrix.entries[0].case_id == "Brand:default:default:light:390"
    assert element_metadata_manifest()["schema"] == "hedron.element-metadata/1"


def test_theme_export_is_deterministic_and_round_trippable() -> None:
    first = export_theme(default_theme())
    second = export_theme(default_theme())

    assert first.css == second.css
    assert first.json == second.json
    payload = json.loads(first.json)
    assert payload["schema"] == "hedron.theme-resolution/1"
    assert payload["fingerprint"] == first.resolution.fingerprint
    assert first.conformance["ok"] is True


def test_stylesheet_inspection_covers_bundled_default_consumers() -> None:
    css_path = Path("packages/hedron-core/src/hedron_core/static/hedron-default.css")
    inspection = inspect_theme_css(css_path.read_text(encoding="utf-8"))

    assert inspection["consumer_count"] > 0
    assert inspection["bridged"] is True
    assert inspection["unbridged"] == []


def test_theme_contract_report_contains_shared_evidence() -> None:
    report = theme_contract_report(Theme(name="fixture", tokens=dict(default_theme().tokens)))

    assert report["schema"] == "hedron.theme-contract/1"
    assert report["theme"]["name"] == "fixture"
    assert report["component_manifest"]["digest"]
    assert report["state_matrix"]["count"] > 0
    assert report["digest"]

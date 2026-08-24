"""Executable evidence for phase 0.63 profiler, checks, migration, and identity."""

from __future__ import annotations

import json
from pathlib import Path

from hedron import AccountSummary, Brand, package_identity_manifest, render
from hedron.migrate.react import analyze_react_source, migration_disposition_manifest
from hedron.phase063_checks import analyze_project
from hedron_core import ActionTrace, StyleRecipe, build_state_matrix, profile_interaction_trace
from hedron_core.trace_contract import encode_interaction_trace


def test_profiler_exposes_bounded_public_timeline_without_payloads() -> None:
    trace = ActionTrace().append(
        "pending",
        facts={
            "component": "Button",
            "action": "save",
            "request": "req-1",
            "duration_ms": 12.5,
            "private_payload": {"password": "secret"},
        },
    )
    profile = profile_interaction_trace(encode_interaction_trace(trace))

    assert profile["timing"]["samples"] == 1
    assert profile["timeline"][0]["facts"] == {
        "action": "save",
        "component": "Button",
        "request": "req-1",
    }
    assert "private_payload" not in json.dumps(profile)


def test_phase063_checks_are_non_executing_deterministic_and_source_linked(tmp_path: Path) -> None:
    (tmp_path / "app.tsx").write_text("const value = eval(input);\n", encoding="utf-8")
    first = analyze_project(tmp_path)
    second = analyze_project(tmp_path)

    assert first == second
    assert first["non_executing"] is True
    assert first["findings"][0]["code"] == "HED-CHECK-0003"
    assert first["findings"][0]["span"]["path"] == "app.tsx"


def test_react_migration_reports_explicit_dispositions_and_spans(tmp_path: Path) -> None:
    source = tmp_path / "Dashboard.tsx"
    source.write_text(
        "function Dashboard() { useOptimistic(0); return <canvas />; }\n", encoding="utf-8"
    )
    report = analyze_react_source(source)
    dispositions = {item["disposition"] for item in report["findings"]}

    assert report["non_executing"] is True
    assert dispositions == {"adapter", "unsupported"}
    assert all(item["span"]["path"] == "Dashboard.tsx" for item in report["findings"])
    assert migration_disposition_manifest()["non_executing"] is True


def test_package_identity_matches_registry_metadata() -> None:
    report = package_identity_manifest()

    assert report["schema"] == "hedron.package-identity/1"
    assert report["runtime"] == "python-no-node"
    assert report["component_manifest_digest"]
    assert report["metadata_digest"]
    assert report["digest"]


def test_responsive_recipe_conditions_are_finite_and_provider_neutral() -> None:
    recipe = StyleRecipe.surface(
        "responsive-panel",
        appearance="raised",
        responsive={"padding": {"base": "sm", "md": "lg"}},
    )

    assert recipe.responsive_markers() == {
        "hedron-recipe-padding-base": "sm",
        "hedron-recipe-padding-md": "lg",
    }


def test_state_matrix_ids_include_non_default_accessibility_modes() -> None:
    matrix = build_state_matrix(
        components=("Button",),
        viewports=("390",),
        modes=("light",),
        accessibility_modes=("none", "forced-colors"),
    )

    assert len({entry.case_id for entry in matrix.entries}) == len(matrix.entries)
    assert any(entry.case_id.endswith(":forced-colors") for entry in matrix.entries)


def test_identity_marks_have_bounded_themeable_contracts() -> None:
    brand = Brand("Hedron", mark_text="H", mark_size="lg", mark_shape="circle", mark_tone="neutral")
    account = AccountSummary("Ada", mark_text="A", mark_size="sm")

    brand_html = render(brand).html
    account_html = render(account).html
    assert 'data-hedron-mark-size="lg"' in brand_html
    assert 'data-hedron-mark-shape="circle"' in brand_html
    assert 'data-hedron-mark-tone="neutral"' in brand_html
    assert 'data-hedron-mark-size="sm"' in account_html

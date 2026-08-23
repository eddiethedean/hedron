"""Executable release-evidence corpus for the phase 0.59 contract.

These tests are intentionally cross-cutting: each one exercises a public
surface and its static fallback/serialization contract, so a passing unit
check is evidence for the gate it names rather than only a packet-shape check.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from hedron import (
    AccountSummary,
    AppShell,
    Brand,
    Button,
    Container,
    ConnectorFlow,
    ConnectorNode,
    ConnectorTrack,
    Dialog,
    EnvironmentBanner,
    FlowStep,
    Fragment,
    LinkButton,
    NavStatus,
    Popover,
    ProcessFlow,
    Stack,
    Text,
    Theme,
    render,
)
from hedron_core import compile_css
from hedron_core.bundles import FeatureBundle, eject_source
from hedron_core.codes import HED_CSS_REMOTE
from hedron_core.diagnostics import HedronError
from hedron_core.manifests import CssSymbolManifest, canonical_json
from hedron_core.theme import contrast_diagnostics, emit_theme_css, default_theme, compile_palette


ROOT = Path(__file__).parents[2]
CSS = ROOT / "packages/hedron-core/src/hedron_core/static/hedron-default.css"


def test_compiler_release_corpus_covers_import_assets_and_versioned_manifests(
    tmp_path: Path,
) -> None:
    (tmp_path / "theme.css").write_text(".imported { color: red; }\n", encoding="utf-8")
    (tmp_path / "icon.svg").write_text("<svg></svg>\n", encoding="utf-8")
    source = (
        '@import "theme.css"; '
        '@keyframes pulse { from { opacity: 0; } to { opacity: 1; } } '
        '.root { background: url("icon.svg"); animation: pulse 1s; }'
    )
    result = compile_css(
        source,
        component_id="release059",
        registered_roots=[tmp_path],
        component_dir=tmp_path,
    )
    assert result.manifest.format_version == 2
    assert result.asset_urls == ("icon.svg",)
    assert result.manifest.keyframes["pulse"].startswith("h-")
    assert "theme.css" in result.css and "@layer components" in result.css
    assert result.css == compile_css(
        source,
        component_id="release059",
        registered_roots=[tmp_path],
        component_dir=tmp_path,
    ).css
    legacy = CssSymbolManifest(
        format_version=1,
        component_id="release059",
        symbols={"root": "h-root-legacy"},
        keyframes={},
    )
    legacy.validate_format()
    assert json.loads(canonical_json(legacy.to_dict()))["format_version"] == 1


def test_compiler_release_corpus_fails_closed_and_redacts_unsafe_inputs(tmp_path: Path) -> None:
    with pytest.raises(HedronError):
        compile_css(".root { color: red;", component_id="release059")
    with pytest.raises(HedronError):
        compile_css("html { color: red; }", component_id="release059")
    with pytest.raises(HedronError) as remote:
        compile_css(
            ".root { background: url(https://example.invalid/a); }",
            component_id="release059",
        )
    assert remote.value.diagnostic.code == HED_CSS_REMOTE
    with pytest.raises(HedronError):
        compile_css(
            ".root { background: url(../secret.svg); }",
            component_id="release059",
            registered_roots=[tmp_path],
            component_dir=tmp_path,
        )


def test_cascade_tokens_and_color_release_matrix_is_deterministic() -> None:
    css = CSS.read_text(encoding="utf-8")
    assert css.startswith("@layer reset, tokens, base, components, utilities, overrides;")
    theme = default_theme()
    emitted = emit_theme_css(theme)
    assert emitted.startswith("@layer tokens {")
    assert emitted == emit_theme_css(theme)
    palette = compile_palette("#2563eb")
    assert not contrast_diagnostics(palette)
    variant = Theme(
        name="release059",
        tokens=dict(theme.tokens),
        modes={name: dict(values) for name, values in theme.modes.items()},
        variants={"dense": {"space.unit": "0.25rem"}},
    )
    variant_css = emit_theme_css(variant)
    assert '[data-hedron-theme="release059"][data-hedron-variant="dense"]' in variant_css
    assert "--hedron-space-unit: 0.25rem" in variant_css


def test_container_layout_and_intrinsic_content_release_matrix() -> None:
    rendered = render(
        Container(
            Stack(
                Text("unbroken-content", overflow="break", lines=2),
                gap="1rem",
            ),
            query="inline-size",
            name="panel",
        )
    ).html
    assert 'data-hedron-container-query="inline-size"' in rendered
    assert 'data-hedron-container-name="panel"' in rendered
    assert 'data-hedron-overflow="break"' in rendered
    assert 'data-hedron-lines="2"' in rendered
    css = CSS.read_text(encoding="utf-8")
    for marker in (
        "@supports (container-type: inline-size)",
        "inline-size:",
        "block-size:",
        "max-inline-size: 100%",
        "overflow-wrap: anywhere",
    ):
        assert marker in css


def test_workflow_connector_release_matrix_is_provider_neutral_and_reduced_motion_safe() -> None:
    rendered = render(
        ConnectorFlow(
            ConnectorNode("Source", kind="source", state="ready", detail="MSS"),
            ConnectorTrack(Text("Extract"), label="Transfer stages", active=True),
            ConnectorNode("Destination", kind="target", state="blocked", detail="Postgres"),
            direction="vertical",
        )
    ).html
    for marker in (
        'data-hedron-connector-flow="true"',
        'data-hedron-connector-direction="vertical"',
        'data-hedron-connector-node="true"',
        'data-hedron-connector-kind="source"',
        'data-hedron-connector-state="blocked"',
        'data-hedron-connector-track="true"',
        'data-hedron-connector-active="true"',
    ):
        assert marker in rendered
    css = CSS.read_text(encoding="utf-8")
    assert ".hedron-connector-track" in css
    assert "prefers-reduced-motion" in css


def test_control_and_security_release_matrix_uses_native_safe_attribute_seam() -> None:
    rendered = render(
        Fragment(
            Button("Save", size="lg", width="full", attrs={"aria-describedby": "hint"}),
            LinkButton("Open", "/open", size="sm", width="content", attrs={"data-test": "x"}),
        )
    ).html
    assert '<button ' in rendered and 'aria-describedby="hint"' in rendered
    assert '<a ' in rendered and 'data-test="x"' in rendered
    with pytest.raises(ValueError, match="unsafe typed control"):
        render(Button("Bad", attrs={"onclick": "alert(1)"}))
    with pytest.raises(ValueError, match="owned by the component"):
        render(LinkButton("Bad", "/safe", attrs={"href": "/override"}))


def test_shell_workflow_and_accessibility_release_matrix_is_semantic() -> None:
    shell = AppShell(
        brand=Brand("Hedron", href="/"),
        env_badge=EnvironmentBanner("Staging", tone="warning"),
        account=AccountSummary("Ada", detail="ada@example.test", href="/account"),
        nav=Text("Dashboard"),
        nav_footer=NavStatus("Connected", tone="success"),
        body=ProcessFlow(
            FlowStep("Extract", status="complete"),
            FlowStep("Transform", status="current", description="Running"),
            FlowStep("Load", status="pending"),
            label="Data pipeline",
            direction="vertical",
        ),
        app_footer=Text("Footer"),
    )
    rendered = render(shell).html
    for marker in (
        'data-hedron-app-shell="true"',
        'data-hedron-brand="true"',
        'data-hedron-app-env="true"',
        'data-hedron-account-summary="true"',
        'data-hedron-process-flow="true"',
        'aria-current="step"',
        'data-hedron-nav-status="true"',
        '<main',
        '<nav',
    ):
        assert marker in rendered


@pytest.mark.parametrize("placement", ("block-start", "block-end", "inline-start", "inline-end", "center"))
@pytest.mark.parametrize("mode", ("popover", "details"))
def test_overlay_release_matrix_has_native_and_document_flow_fallbacks(
    placement: str, mode: str
) -> None:
    rendered = render(
        Popover(
            Text("Menu"),
            mode=mode,  # type: ignore[arg-type]
            placement=placement,  # type: ignore[arg-type]
            collision="static",
        )
    ).html
    assert f'data-hedron-popover-placement="{placement}"' in rendered
    assert 'data-hedron-popover-collision="static"' in rendered
    assert ("<details" in rendered) is (mode == "details")
    dialog = render(Dialog("Confirm", Text("Continue"), open=True, id="confirm")).html
    assert '<dialog ' in dialog and 'aria-labelledby="confirm-title"' in dialog
    assert 'formmethod="dialog"' in dialog


def test_motion_media_typography_and_a11y_release_matrix_is_static_css_complete() -> None:
    css = CSS.read_text(encoding="utf-8")
    for marker in (
        "@media (prefers-reduced-motion: reduce)",
        "@media (prefers-contrast: more)",
        "@media (forced-colors: active)",
        "@media print",
        ":focus-visible",
        "safe-area-inset-bottom",
        "100svh",
        "-webkit-line-clamp: 1",
        "overflow-wrap: anywhere",
        "@supports (anchor-name: --hedron-popover)",
    ):
        assert marker in css


def test_dx_ejection_and_visual_serialization_are_reviewable() -> None:
    bundle = FeatureBundle(
        logical_id="demo.feature",
        provider="demo-provider",
        provider_version="1.0",
        views=("demo.view",),
        commands=("demo.command",),
        limitations=("static fixture",),
    )
    source = eject_source(bundle)
    assert "demo.feature" in source
    assert "demo.view" in source and "demo.command" in source
    assert "serialized workflow executor" in source
    first = render(Text("stable", lines=2)).html
    second = render(Text("stable", lines=2)).html
    assert first == second


def test_release_evidence_artifacts_are_present_and_machine_readable() -> None:
    evidence = ROOT / "docs/acceptance/evidence-059"
    for name in (
        "baseline-0581.json",
        "parser-recipe-059.json",
        "capability-chromium-059.json",
        "capability-firefox-059.json",
        "capability-webkit-059.json",
        "performance-059.json",
        "package-059.json",
        "consumer-059.json",
        "release-matrix-059.json",
    ):
        payload = json.loads((evidence / name).read_text(encoding="utf-8"))
        assert isinstance(payload, dict)
    consumer = json.loads((evidence / "consumer-059.json").read_text(encoding="utf-8"))
    assert consumer["suite"] == "full"
    assert consumer["returncode"] == 0
    assert consumer["passed"] == consumer["collected"]

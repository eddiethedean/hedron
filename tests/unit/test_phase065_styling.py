from __future__ import annotations

from hedron_core.builtins import (
    AppShell,
    Card,
    FlowStep,
    FormField,
    NavLink,
    ProcessFlow,
    SplitView,
    StyleScope,
    TextInput,
)
from hedron_core.css.compiler import compile_css
from hedron_core.manifests import ApplicationStyleManifest
from hedron_core.presentation_064 import (
    application_style_hook_data,
    application_style_hook_manifest,
    presentation_tokens,
)


def test_phase065_hook_manifest_and_motion_tokens_are_stable() -> None:
    hooks = application_style_hook_manifest()
    assert set(hooks) == {"AppShell", "Card", "FormField", "ProcessFlow", "SplitView"}
    assert hooks["AppShell"]["parts"]["nav.link"]["states"] == [
        "default",
        "hover",
        "current",
        "disabled",
    ]
    tokens = presentation_tokens()
    assert all(
        f"{name}" in tokens
        for name in (
            "motion.instant",
            "motion.standard",
            "motion.emphasized",
            "motion.reveal",
            "motion.elevate",
            "motion.crossfade",
        )
    )


def test_phase065_builtin_markers_cover_required_surfaces() -> None:
    shell = AppShell(nav=NavLink("Home", "/home", active=True)).render()
    nav = shell.children[0]
    link = nav.children[0].render()
    assert link.attributes["data-hedron-component"] == "AppShell"
    assert link.attributes["data-hedron-state"] == "current"

    card = Card("content", title="Heading", footer="metadata").render()
    assert card.children[0].attributes["data-hedron-part"] == "heading"
    assert card.children[1].attributes["data-hedron-part"] == "supporting-copy"
    assert card.children[2].attributes["data-hedron-part"] == "metadata"

    field = FormField(
        name="email", label="Email", control=TextInput("email"), error="Invalid"
    ).render()
    assert field.children[1].attributes["data-hedron-part"] == "control"
    assert field.children[1].attributes["data-hedron-state"] == "invalid"

    step = ProcessFlow(FlowStep("Deploy", status="complete"), label="Release").render()
    step_node = step.children[0].render()
    assert step_node.attributes["data-hedron-component"] == "ProcessFlow"
    assert step_node.attributes["data-hedron-state"] == "complete"

    split = SplitView("A", "B").render()
    assert split.children[1].attributes["data-hedron-part"] == "separator"

    scoped = StyleScope("content", scope="workspace").render()
    assert scoped.attributes["data-hedron-style-scope"] == "workspace"


def test_phase065_css_scope_rewrite_and_manifest() -> None:
    result = compile_css(
        ".card, .card:hover { color: red; }",
        component_id="application:workspace",
        layer="application",
        scope_root=':where([data-hedron-style-scope="workspace"])',
        rewrite_selectors=False,
    )
    assert ':where([data-hedron-style-scope="workspace"])' in result.css
    assert ".card" in result.css
    assert "@layer application" in result.css
    assert result.manifest.component_id == "application:workspace"


def test_phase065_application_style_manifest_round_trip() -> None:
    manifest = ApplicationStyleManifest(
        format_version=1,
        entries=({"logical_id": "application:style:workspace"},),
        source_map={"application:style:workspace": {"line_count": 1}},
    )
    restored = ApplicationStyleManifest.from_dict(manifest.to_dict())
    restored.validate_format()
    assert restored.entries == manifest.entries
    assert restored.digest == manifest.to_dict()["digest"]


def test_phase065_hook_data_rejects_private_or_unknown_states() -> None:
    assert (
        application_style_hook_data("Card", "heading", state="default")["hedron-part"] == "heading"
    )
    try:
        application_style_hook_data("Card", "private", state="default")
    except ValueError as exc:
        assert "unknown application style hook" in str(exc)
    else:  # pragma: no cover - assertion clarity
        raise AssertionError("private hooks must be rejected")

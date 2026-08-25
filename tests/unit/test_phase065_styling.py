from __future__ import annotations

import pytest

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
from hedron_core.diagnostics import HedronError
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


def test_phase065_scope_preserves_nested_selector_commas() -> None:
    result = compile_css(
        '.card:is(.primary, .secondary), .card:not([data-kind="a,b"]) { color: red; }',
        component_id="application:workspace",
        layer="application",
        scope_root=':where([data-hedron-style-scope="workspace"])',
        rewrite_selectors=False,
    )
    assert (
        ':where([data-hedron-style-scope="workspace"]) .card:is(.primary, .secondary)' in result.css
    )
    assert (
        ':where([data-hedron-style-scope="workspace"]) .card:not([data-kind="a,b"])' in result.css
    )


def test_phase065_rejects_quoted_remote_imports() -> None:
    with pytest.raises(HedronError, match="Remote CSS import rejected"):
        compile_css(
            '@import "https://example.com/theme.css"; .card { color: red; }',
            component_id="application:workspace",
            layer="application",
            rewrite_selectors=False,
        )


def test_phase065_rejects_escaped_remote_imports_and_honors_remote_opt_in(tmp_path) -> None:
    with pytest.raises(HedronError, match="Remote CSS import rejected"):
        compile_css(
            '@import "h\\74 tps://example.com/theme.css";',
            component_id="application:workspace",
            layer="application",
            rewrite_selectors=False,
        )
    with pytest.raises(HedronError, match="Remote CSS import rejected"):
        compile_css(
            '@import "ht\\\ntps://example.com/theme.css";',
            component_id="application:workspace",
            layer="application",
            rewrite_selectors=False,
        )

    decoy = tmp_path / r"h\74 tps:" / "example.com"
    decoy.mkdir(parents=True)
    (decoy / "image.png").write_bytes(b"local decoy")
    with pytest.raises(HedronError, match="Remote CSS URL rejected"):
        compile_css(
            r".card { background-image: url(h\74 tps://example.com/image.png); }",
            component_id="application:workspace",
            layer="application",
            registered_roots=(tmp_path,),
            component_dir=tmp_path,
            rewrite_selectors=False,
        )
    result = compile_css(
        '@import "https://example.com/theme.css";',
        component_id="component:workspace",
        layer="components",
        allow_remote=True,
        rewrite_selectors=False,
    )
    assert "https://example.com/theme.css" in result.css


def test_phase065_ejection_write_path_rejects_symlinked_destinations(tmp_path) -> None:
    from hedron.cli.commands.style import _assert_project_write_path

    project = tmp_path / "project"
    outside = tmp_path / "outside"
    project.mkdir()
    outside.mkdir()
    with pytest.raises(ValueError, match="outside the project root"):
        _assert_project_write_path(
            project / ".." / "outside" / "application-styles.css",
            cwd=project,
        )

    link = project / "output"
    link.symlink_to(outside, target_is_directory=True)
    with pytest.raises(ValueError, match="symlink"):
        _assert_project_write_path(link / "application-styles.css", cwd=project)


def test_phase065_ejection_manifest_fails_closed_when_integrity_fields_are_missing(
    tmp_path,
) -> None:
    import json

    from hedron.cli.commands.style import _application_style_drift

    manifest = tmp_path / "source_map.json"
    manifest.write_text(
        json.dumps({"schema": "hedron.style-ejection/1", "styles": []}),
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="requires two local file names"):
        _application_style_drift(manifest)


def test_phase065_rejects_private_and_behavior_application_css() -> None:
    with pytest.raises(HedronError, match="Private Hedron selector rejected"):
        compile_css(
            ".hedron-card .internal { color: red; }",
            component_id="application:workspace",
            layer="application",
            rewrite_selectors=False,
        )
    with pytest.raises(HedronError, match="Behavior-changing CSS rejected"):
        compile_css(
            ".card { pointer-events: none; }",
            component_id="application:workspace",
            layer="application",
            rewrite_selectors=False,
        )


def test_phase065_requires_explicit_global_css_opt_in() -> None:
    with pytest.raises(HedronError, match="Global selector requires explicit opt-in"):
        compile_css(
            ":global(body) { color: red; }",
            component_id="application:workspace",
            layer="application",
            rewrite_selectors=False,
        )
    result = compile_css(
        "body { color: red; }",
        component_id="application:workspace",
        layer="application",
        rewrite_selectors=False,
        allow_global=True,
    )
    assert "body" in result.css


def test_phase065_application_style_source_policy_rejects_symlink_and_escape(tmp_path) -> None:
    from hedron_core.registry.application_style import register_application_style

    source = tmp_path / "app.css"
    source.write_text(".card { color: red; }", encoding="utf-8")
    link = tmp_path / "link.css"
    link.symlink_to(source)
    with pytest.raises(ValueError, match="symlinks"):
        register_application_style(
            name="symlink-policy",
            source=link,
            scope="workspace",
            allowed_roots=(tmp_path,),
        )
    with pytest.raises(ValueError, match="allowed local package root"):
        register_application_style(
            name="root-policy",
            source=source,
            scope="workspace",
            allowed_roots=(tmp_path / "other",),
        )


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


def test_phase065_dotted_public_hook_compiles_as_an_or_state_selector() -> None:
    from hedron_core import ScopedStyleRecipe, compile_scoped_styles

    recipe = ScopedStyleRecipe(
        component="AppShell",
        part="nav.link",
        states=("current", "disabled"),
        declarations={"opacity": "0.5"},
    )
    css = compile_scoped_styles((recipe,)).css
    assert "nav.link" not in recipe.class_name
    assert f".{recipe.class_name}:is(" in css
    assert '[data-hedron-state~="current"]' in css
    assert '[data-hedron-state~="disabled"]' in css

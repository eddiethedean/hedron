"""Deterministic phase 0.59 contract matrix for the implemented public surface."""

from __future__ import annotations

from pathlib import Path

import pytest

from hedron import Button, Container, Fragment, LinkButton, Popover, StyleScope, Text, Theme, render
from hedron_core import compile_css, scoped_identifier
from hedron_core.diagnostics import HedronError
from hedron_core.manifests import CssSymbolManifest


@pytest.mark.parametrize(
    "source",
    (
        ".root { color: red; }",
        "@media (width > 40rem) { .root { color: red; } }",
        "@supports (display: grid) { .root { display: grid; } }",
        "@container (min-width: 20rem) { .root { color: red; } }",
        "@scope (.root) { .title { color: red; } }",
        "@layer components { .root { color: red; } }",
    ),
)
def test_compiler_matrix_preserves_modern_rule_boundaries(source: str) -> None:
    result = compile_css(source, component_id="matrix059")
    assert result.manifest.format_version == 2
    assert "matrix059" not in result.css
    assert all(scoped in result.css for scoped in result.manifest.symbols.values())


def test_compiler_matrix_handles_animation_strings_comments_and_local_import(
    tmp_path: Path,
) -> None:
    (tmp_path / "theme.css").write_text(".imported { color: red; }", encoding="utf-8")
    source = (
        '@import "theme.css"; /* .comment */ '
        "@keyframes fade { from { opacity: 0; } to { opacity: 1; } } "
        '.root { content: ".literal"; animation: fade 200ms ease; }'
    )
    result = compile_css(
        source,
        component_id="matrix059-import",
        registered_roots=[tmp_path],
        component_dir=tmp_path,
    )
    assert "theme.css" in result.css
    assert 'content: ".literal"' in result.css
    assert result.manifest.keyframes["fade"].startswith("h-")
    assert "css" not in result.manifest.symbols


def test_compiler_matrix_rejects_unsafe_globals_urls_and_malformed_input(tmp_path: Path) -> None:
    with pytest.raises(HedronError):
        compile_css("html { color: red; }", component_id="matrix059-global")
    with pytest.raises(HedronError):
        compile_css(
            ".root { background: url(https://evil.example/a); }", component_id="matrix059-url"
        )
    with pytest.raises(HedronError):
        compile_css(".root { color: red;", component_id="matrix059-malformed")
    with pytest.raises(HedronError):
        compile_css(
            ".root { background: url(../secret.png); }",
            component_id="matrix059-traversal",
            component_dir=tmp_path,
        )


def test_compiler_matrix_is_deterministic_and_manifest_readers_are_compatible() -> None:
    first = compile_css(".root { color: red; }", component_id="matrix059")
    second = compile_css(".root { color: red; }", component_id="matrix059")
    assert first.css == second.css
    assert first.manifest.to_dict() == second.manifest.to_dict()
    legacy = CssSymbolManifest(
        format_version=1,
        component_id="matrix059",
        symbols={"root": scoped_identifier("matrix059", "root")},
        keyframes={},
    )
    legacy.validate_format()


def test_tokens_theme_and_scope_matrix_is_explicit_and_additive() -> None:
    from hedron_core.theme import default_theme

    base = default_theme()
    theme = Theme(
        name="matrix",
        tokens=dict(base.tokens),
        modes={key: dict(value) for key, value in base.modes.items()},
        variants={**base.variants, "dense": {"space.unit": "0.25rem"}},
    )
    from hedron_core.theme import emit_theme_css

    rendered = render(StyleScope(Text("content"), theme="default", variant="dense")).html
    assert 'data-hedron-theme="default"' in rendered
    assert 'data-hedron-variant="dense"' in rendered
    assert "--hedron-space-unit: 0.25rem" in emit_theme_css(theme)


@pytest.mark.parametrize(
    ("query", "name", "marker"),
    (
        ("none", None, "data-hedron-container-query"),
        ("inline-size", None, "data-hedron-container-query"),
        ("inline-size", "panel", "data-hedron-container-name"),
    ),
)
def test_layout_matrix_preserves_opt_in_container_markers(
    query: str, name: str | None, marker: str
) -> None:
    rendered = render(Container(Text("content"), query=query, name=name)).html
    if query == "none":
        assert marker not in rendered
    else:
        assert marker in rendered
        assert "content" in rendered


def test_control_matrix_covers_size_width_icons_and_safe_native_attributes() -> None:
    rendered = render(
        Fragment(
            Button("Save", size="sm", width="full", attrs={"title": "Save", "hx-post": "/save"}),
            LinkButton("Open", "/open", size="sm", width="full", attrs={"aria-label": "Open"}),
        )
    ).html
    assert 'data-hedron-size="sm"' in rendered
    assert 'data-hedron-width="full"' in rendered
    assert 'hx-post="/save"' in rendered
    assert 'aria-label="Open"' in rendered


def test_overlay_and_media_matrix_has_bounded_markers_and_static_css_fallbacks() -> None:
    rendered = render(Popover(Text("Menu"), placement="block-end", collision="flip")).html
    assert 'data-hedron-popover-placement="block-end"' in rendered
    assert 'data-hedron-popover-collision="flip"' in rendered
    css = (
        Path(__file__).parents[2] / "packages/hedron-core/src/hedron_core/static/hedron-default.css"
    ).read_text(encoding="utf-8")
    for marker in (
        "@media print",
        "prefers-reduced-motion",
        "prefers-contrast",
        "safe-area-inset-left",
        "100svh",
    ):
        assert marker in css

"""SCOPE-058 evidence."""

from __future__ import annotations

from importlib import resources

import pytest

from hedron import StyleScope, Text
from hedron_core.diagnostics import HedronError
from hedron_core.rendering import RenderContext, RenderMode, render
from hedron_core.theme import Theme, emit_theme_css


def test_style_scope_emits_data_hedron_markers() -> None:
    html = render(
        StyleScope(
            Text("scoped"),
            theme="default",
            color_mode="dark",
            density="compact",
            variant="dense",
        ),
        context=RenderContext.standalone(),
        mode=RenderMode.FRAGMENT,
    ).html
    assert 'data-hedron-style-scope="true"' in html
    assert 'data-hedron-theme="default"' in html
    assert 'data-hedron-color-mode="dark"' in html
    assert 'data-hedron-density="compact"' in html
    assert 'data-hedron-variant="dense"' in html
    assert 'data-theme="dark"' in html


def test_style_scope_rejects_invalid_density() -> None:
    with pytest.raises(HedronError):
        StyleScope(Text("x"), density="ultra")  # type: ignore[arg-type]


def test_style_scope_rejects_invalid_theme_name() -> None:
    with pytest.raises(HedronError):
        StyleScope(Text("x"), theme="bad theme!")


def test_style_scope_css_contract_present() -> None:
    from hedron_core.theme import ensure_builtin_themes_registered, get_theme

    css = (
        resources.files("hedron_core.static")
        .joinpath("hedron-default.css")
        .read_text(encoding="utf-8")
    )
    assert ".hedron-style-scope[data-hedron-density=" in css
    ensure_builtin_themes_registered()
    meta = get_theme("default")
    assert meta is not None
    theme_css = emit_theme_css(
        Theme(
            name="scoped",
            tokens=dict(meta.tokens),
            modes={k: dict(v) for k, v in meta.modes.items()},
            variants={k: dict(v) for k, v in meta.variants.items()},
        )
    )
    assert '[data-hedron-theme="scoped"][data-hedron-color-mode="dark"]' in theme_css


def test_theme_variants_emit_only_with_explicit_marker() -> None:
    from hedron_core.theme import default_theme

    meta = default_theme()
    theme = Theme(
        name="variant059",
        tokens=dict(meta.tokens),
        modes={k: dict(v) for k, v in meta.modes.items()},
        variants={"dense": {"space.unit": "0.25rem"}},
    )
    css = emit_theme_css(theme)
    assert '[data-hedron-theme="variant059"][data-hedron-variant="dense"]' in css
    assert "--hedron-space-unit: 0.25rem" in css

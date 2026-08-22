"""Focused 0.59 compiler, theme, and typed-control contracts."""

from __future__ import annotations

import pytest

from hedron import Button, LinkButton, Popover, StyleScope, Text, render
from hedron_core.diagnostics import HedronError


def test_typed_controls_forward_safe_attrs_to_native_element() -> None:
    button = render(
        Button(
            "Save",
            attrs={
                "title": "Save changes",
                "aria-controls": "editor",
                "data-test-id": "save",
                "hx-post": "/save",
                "popovertarget": "dialog",
            },
        )
    ).html
    assert "<button " in button
    assert 'title="Save changes"' in button
    assert 'aria-controls="editor"' in button
    assert 'data-test-id="save"' in button
    assert 'hx-post="/save"' in button
    assert 'popovertarget="dialog"' in button


def test_typed_controls_reject_unsafe_or_structural_attrs() -> None:
    with pytest.raises(ValueError, match="unsafe typed control"):
        render(Button("Save", attrs={"onclick": "alert(1)"}))
    with pytest.raises(ValueError, match="unsafe typed control"):
        render(Button("Save", attrs={"hx-on:click": "alert(1)"}))
    with pytest.raises(ValueError, match="malformed ARIA"):
        render(Button("Save", attrs={"aria-": "bad"}))
    with pytest.raises(ValueError, match="owned by the component"):
        render(LinkButton("Go", "/go", attrs={"href": "/unsafe-override"}))


def test_style_scope_variant_is_explicit_and_validated() -> None:
    rendered = render(StyleScope(Text("dense"), variant="dense")).html
    assert 'data-hedron-variant="dense"' in rendered
    with pytest.raises(HedronError):
        StyleScope(Text("bad"), variant="bad variant")


def test_popover_placement_and_collision_are_bounded_markers() -> None:
    rendered = render(Popover(Text("Menu"), placement="inline-end", collision="shift")).html
    assert 'data-hedron-popover-placement="inline-end"' in rendered
    assert 'data-hedron-popover-collision="shift"' in rendered

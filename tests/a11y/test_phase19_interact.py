"""Phase 0.19 INTERACT-019."""

from __future__ import annotations

from hedron_core import Button, Dialog, Form, FormField, TextInput, render
from hedron_core.a11y import TargetSpacingPolicy


def test_target_spacing_policy_defaults() -> None:
    policy = TargetSpacingPolicy()
    assert policy.min_target_css_px == 24
    assert policy.allow_spacing_exception is True


def test_interactive_controls_keyboard_names() -> None:
    html = render(Button("Save")).html
    assert "<button" in html and "Save" in html
    field = FormField(name="email", label="Email", control=TextInput("email"), required=True)
    form_html = render(Form(field)).html
    assert "aria-required" in form_html or "required" in form_html
    dlg = render(Dialog("Edit", Form(field))).html
    assert "dialog" in dlg.lower() or "role=" in dlg

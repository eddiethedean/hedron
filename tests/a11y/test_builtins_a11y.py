"""Accessibility core checks for 0.1 built-ins."""

from __future__ import annotations

import pytest

from hedron_core import (
    Button,
    Checkbox,
    Form,
    FormField,
    Heading,
    IconButton,
    Main,
    Nav,
    TextInput,
    render,
)


@pytest.mark.a11y
def test_landmarks_use_semantic_elements() -> None:
    html = render(Main(Nav(Heading("Menu", level=2)))).html
    assert "<main>" in html
    assert "<nav>" in html
    assert "<h2>" in html


@pytest.mark.a11y
def test_form_field_label_association() -> None:
    control = TextInput("email", type="email")
    field = FormField(name="email", label="Email", control=control, required=True)
    html = render(Form(field)).html
    assert 'for="field-email"' in html
    assert 'id="field-email"' in html
    assert "<label" in html


@pytest.mark.a11y
def test_button_has_accessible_name() -> None:
    html = render(Button("Save")).html
    assert ">Save</button>" in html
    icon = render(IconButton("Close", icon="×")).html
    assert 'aria-label="Close"' in icon


@pytest.mark.a11y
def test_checkbox_has_label() -> None:
    html = render(Checkbox("tos", "I agree")).html
    assert "<label" in html
    assert 'type="checkbox"' in html

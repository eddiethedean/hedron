"""Accessibility core checks for 0.1 built-ins."""

from __future__ import annotations

import re

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
def test_form_field_label_association_and_aria() -> None:
    control = TextInput("email", type="email", id="custom-ignored")
    field = FormField(
        name="email",
        label="Email",
        control=control,
        required=True,
        help="Work email",
        error="Required",
    )
    html = render(Form(field)).html
    match = re.search(r'<label for="([^"]+)">Email</label>', html)
    assert match is not None
    field_id = match.group(1)
    assert field_id.startswith("field-email-")
    assert f'id="{field_id}"' in html
    assert f'aria-describedby="{field_id}-help {field_id}-error"' in html
    assert 'aria-invalid="true"' in html
    assert 'aria-required="true"' in html
    assert "required" in html
    assert 'id="custom-ignored"' not in html


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


@pytest.mark.a11y
def test_form_field_checkbox_aria_on_input_not_wrapper() -> None:
    field = FormField(
        name="tos",
        label="Terms",
        control=Checkbox("tos", "I agree"),
        required=True,
        error="Required",
    )
    html = render(Form(field)).html
    # Outer FormField label is omitted for Checkbox; control keeps its own label.
    assert html.count("<label") == 1
    assert 'type="checkbox"' in html
    assert 'aria-invalid="true"' in html
    # aria must be on the input, not only a wrapping div without the input attrs.
    assert 'type="checkbox"' in html
    input_idx = html.index('type="checkbox"')
    # Find the input tag containing checkbox and ensure aria-invalid is nearby on same tag.
    tag_start = html.rfind("<input", 0, input_idx)
    tag_end = html.find(">", input_idx)
    input_tag = html[tag_start:tag_end]
    assert 'aria-invalid="true"' in input_tag

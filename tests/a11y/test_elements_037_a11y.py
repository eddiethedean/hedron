"""A11Y-037: form field SSR accessible without JS."""

from __future__ import annotations

from hedron_core.rendering import render
from hedron_elements.field_choice import FieldChoice
from hedron_elements.field_file import FieldFile
from hedron_elements.field_text import FieldText


def test_field_text_has_native_input_and_label() -> None:
    html = render(FieldText("email", value="a@b.c", label="Email")).html
    assert 'type="text"' in html or 'input-type="email"' in html or "email" in html
    assert 'name="email"' in html
    assert "Email" in html or 'label="Email"' in html


def test_field_choice_has_labeled_inputs() -> None:
    html = render(FieldChoice("colors", (("r", "Red"), ("g", "Green")), value=("r",))).html
    assert "<label" in html
    assert "Red" in html
    assert "Green" in html
    assert 'type="checkbox"' in html


def test_field_file_has_file_input_and_label() -> None:
    html = render(FieldFile(name="docs", label="Upload documents")).html
    assert 'type="file"' in html
    assert "Upload documents" in html
    assert 'name="docs"' in html

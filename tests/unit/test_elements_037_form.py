"""FORM-037: form-associated elements render with form_contract."""

from __future__ import annotations

from hedron_core.registry import get_registry, reset_registry_for_tests
from hedron_core.rendering import render
from hedron_elements.field_choice import FieldChoice
from hedron_elements.field_file import FieldFile
from hedron_elements.field_text import FieldText
from hedron_elements.form_contracts import (
    FIELD_CHOICE_CONTRACT,
    FIELD_FILE_CONTRACT,
    FIELD_TEXT_CONTRACT,
)
from hedron_elements.plugin import register


def setup_function() -> None:
    reset_registry_for_tests()


def teardown_function() -> None:
    reset_registry_for_tests()


def _register() -> None:
    class _Ctx:
        def register_diagnostic_owner(self, prefix: str) -> None:
            return None

        def register_feature(self, **kwargs: object) -> None:
            return None

        def register_explorer_panel(self, **kwargs: object) -> None:
            return None

        def register_projection_provider(self, provider: object) -> None:
            return None

    register(_Ctx())  # type: ignore[arg-type]


def test_field_text_ssr_and_contract() -> None:
    _register()
    html = render(FieldText("email", value="a@b.c", label="Email")).html
    assert "hedron-field-text" in html
    assert 'name="email"' in html
    assert 'value="a@b.c"' in html
    assert 'data-hedron-server-region="control"' in html
    meta = get_registry().get_element_definition("hedron-field-text")
    assert meta is not None
    assert meta.form_contract == FIELD_TEXT_CONTRACT


def test_field_choice_ssr_and_contract() -> None:
    _register()
    html = render(
        FieldChoice(
            "tags",
            (("a", "Alpha"), ("b", "Beta")),
            value=("a",),
            choice_type="checkbox",
        )
    ).html
    assert "hedron-field-choice" in html
    assert 'name="tags"' in html
    assert "Alpha" in html
    meta = get_registry().get_element_definition("hedron-field-choice")
    assert meta is not None
    assert meta.form_contract == FIELD_CHOICE_CONTRACT


def test_field_file_ssr_and_contract() -> None:
    _register()
    html = render(FieldFile(name="docs", label="Upload folder", accept=".pdf")).html
    assert "hedron-field-file" in html
    assert 'type="file"' in html
    assert 'name="docs"' in html
    assert 'accept=".pdf"' in html
    meta = get_registry().get_element_definition("hedron-field-file")
    assert meta is not None
    assert meta.form_contract == FIELD_FILE_CONTRACT


def test_399_form_associated_scripts_drop_inner_name() -> None:
    from pathlib import Path

    root = Path(__file__).resolve().parents[2] / "packages/hedron-elements/src/hedron_elements/static"
    text = (root / "hedron-field-text.mjs").read_text(encoding="utf-8")
    choice = (root / "hedron-field-choice.mjs").read_text(encoding="utf-8")
    files = (root / "hedron-field-file.mjs").read_text(encoding="utf-8")
    assert 'removeAttribute("name")' in text
    assert 'removeAttribute("name")' in choice
    assert 'removeAttribute("name")' in files
    assert "new FormData()" in files
    assert "setFormValue?.(input.files)" not in files

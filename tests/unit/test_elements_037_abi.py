"""ABI-037: form_contract validation and 0.37 element registration."""

from __future__ import annotations

import pytest

from hedron_core.diagnostics import HedronError
from hedron_core.element_form import form_contract_dict, validate_form_contract
from hedron_core.registry import get_registry, reset_registry_for_tests
from hedron_elements.form_contracts import (
    FIELD_CHOICE_CONTRACT,
    FIELD_FILE_CONTRACT,
    FIELD_TEXT_CONTRACT,
)
from hedron_elements.plugin import register


@pytest.fixture(autouse=True)
def _reset_registry() -> None:
    reset_registry_for_tests()
    yield
    reset_registry_for_tests()


def test_form_contract_dict_requires_all_keys() -> None:
    contract = form_contract_dict(
        association_mode="single",
        value_encoding="scalar-string",
        reset_policy="native-reset",
        restore_policy="attribute-value",
        validation_mapping="server-authoritative",
        fallback_tag="input",
    )
    assert contract["association_mode"] == "single"
    assert contract["fallback_tag"] == "input"


def test_incomplete_form_contract_rejected() -> None:
    with pytest.raises(HedronError) as exc:
        validate_form_contract({"association_mode": "single"}, tag_name="hedron-field-text")
    assert exc.value.diagnostic.code == "HED-ELEMENT-0007"


def test_form_contract_none_mode_rejected() -> None:
    with pytest.raises(HedronError) as exc:
        validate_form_contract(
            {
                "association_mode": "none",
                "value_encoding": "scalar-string",
                "reset_policy": "native-reset",
                "restore_policy": "attribute-value",
                "validation_mapping": "server-authoritative",
                "fallback_tag": "input",
            },
            tag_name="hedron-field-text",
        )
    assert exc.value.diagnostic.code == "HED-ELEMENT-0007"


def test_plugin_registers_037_elements() -> None:
    class _Ctx:
        def register_diagnostic_owner(self, prefix: str) -> None:
            self.prefix = prefix

        def register_feature(self, **kwargs: object) -> None:
            self.feature = kwargs

        def register_explorer_panel(self, **kwargs: object) -> None:
            return None

        def register_projection_provider(self, provider: object) -> None:
            return None

    ctx = _Ctx()
    register(ctx)  # type: ignore[arg-type]
    reg = get_registry()
    tags = {m.tag_name for m in reg.browser_modules()}
    expected = {
        "hedron-example",
        "hedron-field-text",
        "hedron-field-choice",
        "hedron-field-file",
        "hedron-disclosure",
        "hedron-dialog",
        "hedron-action-async",
    }
    assert expected <= tags
    text = reg.get_element_definition("hedron-field-text")
    assert text is not None
    assert text.form_contract == FIELD_TEXT_CONTRACT
    choice = reg.get_element_definition("hedron-field-choice")
    assert choice is not None
    assert choice.form_contract == FIELD_CHOICE_CONTRACT
    file_el = reg.get_element_definition("hedron-field-file")
    assert file_el is not None
    assert file_el.form_contract == FIELD_FILE_CONTRACT
    assert reg.get_element_definition("hedron-disclosure") is not None
    assert reg.get_element_definition("hedron-dialog") is not None
    assert reg.get_element_definition("hedron-action-async") is not None
    assert ctx.prefix == "HED-ELEMENT-"

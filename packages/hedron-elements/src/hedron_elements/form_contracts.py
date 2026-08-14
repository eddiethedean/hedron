"""Shared form_contract values for 0.37 form-associated reference elements."""

from __future__ import annotations

from hedron_core.element_form import form_contract_dict

FIELD_TEXT_CONTRACT = form_contract_dict(
    association_mode="single",
    value_encoding="scalar-string",
    reset_policy="native-reset",
    restore_policy="attribute-value",
    validation_mapping="server-authoritative",
    fallback_tag="input",
)

FIELD_CHOICE_CONTRACT = form_contract_dict(
    association_mode="multi",
    value_encoding="repeated-name",
    reset_policy="native-reset",
    restore_policy="checked-state",
    validation_mapping="server-authoritative",
    fallback_tag="input",
)

FIELD_FILE_CONTRACT = form_contract_dict(
    association_mode="single",
    value_encoding="file-object",
    reset_policy="native-reset",
    restore_policy="none",
    validation_mapping="server-authoritative",
    fallback_tag="input",
)

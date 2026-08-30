"""#259: draft transfer forbidden fields are exact tokens, not substrings."""

from __future__ import annotations

from pathlib import Path

import pytest

from hedron_elements.transfer import DraftTransferEnvelope

STATIC = (
    Path(__file__).resolve().parents[2]
    / "packages/hedron-elements/src/hedron_elements/static/composition-041.mjs"
)


def _envelope(fields: dict[str, str]) -> DraftTransferEnvelope:
    return DraftTransferEnvelope.create(
        app="a",
        route_family="r",
        element_contract="c",
        schema_version="1",
        subject="s",
        fields=fields,
        operation_id="op1",
        now=100,
    )


def test_benign_field_names_are_allowed() -> None:
    for name in ("secretary", "author"):
        env = _envelope({name: "x"})
        assert env.fields[name] == "x"


def test_exact_forbidden_tokens_still_rejected() -> None:
    with pytest.raises(ValueError, match="forbidden draft field"):
        _envelope({"secret": "x"})
    with pytest.raises(ValueError, match="forbidden draft field"):
        _envelope({"html": "<p>"})
    with pytest.raises(ValueError, match="forbidden draft field"):
        _envelope({"html_preview": "<p>"})


def test_runtime_constructed_identity_fields_must_still_be_strings() -> None:
    envelope = DraftTransferEnvelope(
        app=1,  # type: ignore[arg-type]
        route_family="r",
        element_contract="c",
        schema_version="1",
        subject="s",
        fields={},
        created_at=100,
        expires_at=200,
        operation_id="op1",
    )

    with pytest.raises(ValueError, match="non-empty strings"):
        envelope.validate(now=100)


def test_js_valid_draft_uses_exact_token_set() -> None:
    source = STATIC.read_text(encoding="utf-8")
    assert "forbidden.test(key)" not in source
    assert "forbidden.has(String(key).toLowerCase())" in source

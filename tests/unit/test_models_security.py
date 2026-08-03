"""Unit tests for models, fields, and security types."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from hedron_core import (
    Field,
    FormModel,
    Model,
    Props,
    SafeUrl,
    Secret,
    TrustedHtml,
    UrlPurpose,
)
from hedron_core.diagnostics import HedronError


def test_model_forbids_extra_fields() -> None:
    class User(Model):
        name: str

    with pytest.raises(ValidationError):
        User(name="a", extra="nope")  # type: ignore[call-arg]


def test_secret_redacts_repr_and_str() -> None:
    secret = Secret("super-secret")
    assert "super-secret" not in repr(secret)
    assert "super-secret" not in str(secret)
    assert secret.reveal() == "super-secret"


def test_secret_redacted_in_model_dump() -> None:
    class Row(Model):
        token: Secret[str]

    row = Row(token=Secret("abc"))
    dumped = row.model_dump()
    assert dumped["token"] == "***"
    assert "abc" not in repr(row)


def test_trusted_html_requires_reviewed() -> None:
    with pytest.raises(TypeError):
        TrustedHtml("<b>x</b>")  # type: ignore[call-arg]
    trusted = TrustedHtml.reviewed("<b>x</b>", source="test")
    assert trusted.value == "<b>x</b>"
    assert trusted.source == "test"


def test_safe_url_rejects_javascript() -> None:
    with pytest.raises(HedronError) as exc:
        SafeUrl.parse("javascript:alert(1)", purpose=UrlPurpose.NAVIGATION)
    assert exc.value.diagnostic.code == "HED-SEC-0001"


def test_safe_url_relative_ok() -> None:
    url = SafeUrl.parse("/users/1", purpose=UrlPurpose.NAVIGATION)
    assert url.value == "/users/1"


def test_safe_url_external_requires_flag() -> None:
    with pytest.raises(HedronError):
        SafeUrl.parse("https://example.com", purpose=UrlPurpose.NAVIGATION)
    url = SafeUrl.parse("https://example.com", purpose=UrlPurpose.NAVIGATION, allow_external=True)
    assert url.value.startswith("https://")


def test_field_contradiction() -> None:
    with pytest.raises(HedronError):

        class Bad(FormModel):
            x: int = Field(read_only=True, writable_policy="admin")


def test_props_role() -> None:
    class CardProps(Props):
        title: str = Field(label="Title", min_length=1)

    props = CardProps(title="Hello")
    assert props.title == "Hello"
    assert CardProps._hedron_role == "props"

"""Unit tests for models, fields, and security types."""

from __future__ import annotations

from collections.abc import Callable

import pytest
from pydantic import ValidationError

from hedron_core import (
    Field,
    FormModel,
    HedronError,
    Model,
    Props,
    SafeUrl,
    Secret,
    TrustedHtml,
    UrlPurpose,
)


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


def test_secret_redacted_in_model_dump_and_json() -> None:
    class Row(Model):
        token: Secret[str]
        tokens: list[Secret[str]]

    row = Row(token=Secret("abc"), tokens=[Secret("x"), Secret("y")])
    dumped = row.model_dump()
    assert dumped["token"] == "***"
    assert dumped["tokens"] == ["***", "***"]
    assert "abc" not in row.model_dump_json()
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


def test_field_contradiction_read_only() -> None:
    with pytest.raises(HedronError):

        class Bad(FormModel):
            x: int = Field(read_only=True, writable_policy="admin")


def test_field_secret_identity_contradiction() -> None:
    with pytest.raises(HedronError):

        class Bad(Props):
            password: str = Field(secret=True, identity=True)


def test_field_choices_enforced() -> None:
    class Color(FormModel):
        color: str = Field(choices=["red", "blue"])

    assert Color(color="red").color == "red"
    with pytest.raises(HedronError):
        Color(color="green")


def test_secret_min_length_without_leak() -> None:
    class Cred(FormModel):
        password: Secret[str] = Field(min_length=8, secret=True)

    ok = Cred(password=Secret("longenough"))
    assert ok.password.reveal() == "longenough"
    with pytest.raises(HedronError) as exc:
        Cred(password=Secret("short"))
    assert "short" not in str(exc.value)


def test_rejects_unsupported_annotations() -> None:
    with pytest.raises(HedronError):

        class BadProps(Props):
            cb: Callable[[], None]


def test_props_role() -> None:
    class CardProps(Props):
        title: str = Field(label="Title", min_length=1)

    props = CardProps(title="Hello")
    assert props.title == "Hello"
    assert CardProps._hedron_role == "props"

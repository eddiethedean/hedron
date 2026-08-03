"""Security boundary types: Secret, TrustedHtml, SafeUrl."""

from __future__ import annotations

import html as html_stdlib
import re
from enum import StrEnum
from typing import Any, Generic, TypeVar
from urllib.parse import unquote, urlsplit

from pydantic import GetCoreSchemaHandler
from pydantic_core import core_schema

from hedron_core.diagnostics import HedronError, error

T = TypeVar("T")

_REDACTED = "***"
_DECODE_ROUNDS = 3


class UrlPurpose(StrEnum):
    NAVIGATION = "navigation"
    ASSET = "asset"
    FORM_ACTION = "form_action"
    REDIRECT = "redirect"


class Secret(Generic[T]):
    """Typed sensitive value that never appears in public representations."""

    __slots__ = ("_value",)

    def __init__(self, value: T) -> None:
        object.__setattr__(self, "_value", value)

    def reveal(self) -> T:
        return self._value  # type: ignore[attr-defined]

    def __str__(self) -> str:
        return _REDACTED

    def __repr__(self) -> str:
        return "Secret(***)"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Secret):
            return NotImplemented
        return self.reveal() == other.reveal()

    def __hash__(self) -> int:
        return hash(("Secret", self.reveal()))

    def __getstate__(self) -> dict[str, Any]:
        return {"value": _REDACTED}

    def __setattr__(self, name: str, value: Any) -> None:
        raise AttributeError("Secret is immutable")

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        def validate(value: Any) -> Secret[Any]:
            if isinstance(value, Secret):
                return value
            return Secret(value)

        return core_schema.no_info_plain_validator_function(
            validate,
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda _v: _REDACTED,
                info_arg=False,
                return_schema=core_schema.str_schema(),
            ),
        )


class TrustedHtml:
    """Immutable raw-markup value created only at an explicit trust boundary."""

    __slots__ = ("_value", "_source")

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        raise TypeError("TrustedHtml has no public constructor; use TrustedHtml.reviewed(...)")

    @classmethod
    def reviewed(cls, value: str, *, source: str) -> TrustedHtml:
        if not isinstance(value, str):
            raise TypeError("TrustedHtml value must be a string")
        if not source or not isinstance(source, str):
            raise TypeError("TrustedHtml source must be a non-empty string")
        obj = object.__new__(cls)
        object.__setattr__(obj, "_value", value)
        object.__setattr__(obj, "_source", source)
        return obj

    @property
    def value(self) -> str:
        return self._value  # type: ignore[attr-defined]

    @property
    def source(self) -> str:
        return self._source  # type: ignore[attr-defined]

    def __str__(self) -> str:
        return f"TrustedHtml(source={self.source!r})"

    def __repr__(self) -> str:
        return f"TrustedHtml.reviewed(..., source={self.source!r})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TrustedHtml):
            return NotImplemented
        return self.value == other.value and self.source == other.source

    def __hash__(self) -> int:
        return hash(("TrustedHtml", self.value, self.source))


_DANGEROUS_SCHEMES = frozenset(
    {
        "javascript",
        "vbscript",
        "data",
        "file",
        "blob",
        "about",
    }
)
_CONTROL_CHARS = re.compile(r"[\x00-\x1f\x7f]")
_SCHEME_PREFIX = re.compile(r"^([a-z][a-z0-9+.-]*):", re.IGNORECASE)


def _normalize_for_scheme_scan(value: str) -> str:
    """HTML-unescape and percent-decode (bounded) to defeat scheme smuggling."""
    current = value
    for _ in range(_DECODE_ROUNDS):
        unescaped = html_stdlib.unescape(current)
        try:
            decoded = unquote(unescaped, errors="strict")
        except Exception:
            decoded = unquote(unescaped)
        # Collapse whitespace used to break scheme detection.
        collapsed = re.sub(r"\s+", "", decoded)
        if collapsed == current:
            break
        current = collapsed
    return current.lower()


def _extract_scheme(value: str) -> str:
    match = _SCHEME_PREFIX.match(value)
    return match.group(1).lower() if match else ""


def _purpose_for_attr(attr: str) -> UrlPurpose:
    lower = attr.lower()
    if lower in {"action", "formaction"}:
        return UrlPurpose.FORM_ACTION
    if lower in {"src", "poster"} or lower.endswith("src"):
        return UrlPurpose.ASSET
    if lower in {"hx-get", "hx-post", "hx-put", "hx-patch", "hx-delete", "hx-href"}:
        return UrlPurpose.NAVIGATION
    return UrlPurpose.NAVIGATION


def check_url_purpose_for_attribute(url: SafeUrl, attr: str) -> None:
    """Enforce SafeUrl purpose against the final attribute class."""
    expected = _purpose_for_attr(attr)
    # NAVIGATION may appear on href; REDIRECT is stricter and only for redirect contexts.
    if url.purpose is UrlPurpose.REDIRECT and expected is not UrlPurpose.NAVIGATION:
        raise error(
            "HED-SEC-0006",
            title="URL purpose mismatch",
            explanation=(
                f"SafeUrl purpose={url.purpose.value!r} is not valid for attribute {attr!r}."
            ),
            remediation=f"Parse the URL with purpose={expected.value!r}.",
        )
    if url.purpose is UrlPurpose.ASSET and expected not in {
        UrlPurpose.ASSET,
        UrlPurpose.NAVIGATION,
    }:
        raise error(
            "HED-SEC-0006",
            title="URL purpose mismatch",
            explanation=(
                f"SafeUrl purpose={url.purpose.value!r} is not valid for attribute {attr!r}."
            ),
            remediation=f"Parse the URL with purpose={expected.value!r}.",
        )
    if url.purpose is UrlPurpose.FORM_ACTION and expected is not UrlPurpose.FORM_ACTION:
        raise error(
            "HED-SEC-0006",
            title="URL purpose mismatch",
            explanation=(
                f"SafeUrl purpose={url.purpose.value!r} is not valid for attribute {attr!r}."
            ),
            remediation=f"Parse the URL with purpose={expected.value!r}.",
        )
    if url.purpose is UrlPurpose.NAVIGATION and expected is UrlPurpose.FORM_ACTION:
        raise error(
            "HED-SEC-0006",
            title="URL purpose mismatch",
            explanation="Navigation URLs cannot be used as form actions.",
            remediation="Parse with purpose=form_action.",
        )
    if url.purpose is UrlPurpose.NAVIGATION and expected is UrlPurpose.ASSET:
        raise error(
            "HED-SEC-0006",
            title="URL purpose mismatch",
            explanation="Navigation URLs cannot be used as asset sources.",
            remediation="Parse with purpose=asset.",
        )


class SafeUrl:
    """Validated URL for a declared purpose; still subject to final render policy."""

    __slots__ = ("_value", "_purpose", "_allow_external")

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        raise TypeError("SafeUrl has no public constructor; use SafeUrl.parse(...)")

    @classmethod
    def parse(
        cls,
        value: str,
        *,
        purpose: UrlPurpose,
        allow_external: bool = False,
    ) -> SafeUrl:
        if not isinstance(value, str):
            raise _url_error("URL value must be a string", purpose)
        if _CONTROL_CHARS.search(value):
            raise _url_error("URL contains control characters", purpose)

        raw = value.strip()
        if not raw:
            raise _url_error("URL is empty", purpose)

        if "\\" in raw or "\n" in raw or "\r" in raw or "\t" in raw:
            raise _url_error("URL contains disallowed characters", purpose)

        scanned = _normalize_for_scheme_scan(raw)
        if _CONTROL_CHARS.search(scanned):
            raise _url_error("URL contains control characters after decoding", purpose)

        scanned_scheme = _extract_scheme(scanned)
        if scanned_scheme in _DANGEROUS_SCHEMES:
            raise _url_error(f"Disallowed URL scheme for {purpose.value}", purpose)

        # Also reject dangerous scheme tokens at the start after decode.
        for scheme in _DANGEROUS_SCHEMES:
            if scanned.startswith(f"{scheme}:"):
                raise _url_error(f"Disallowed URL scheme for {purpose.value}", purpose)

        parts = urlsplit(raw)
        scheme = parts.scheme.lower()
        if scheme in _DANGEROUS_SCHEMES:
            raise _url_error(f"Disallowed URL scheme for {purpose.value}", purpose)

        if scheme in {"mailto", "tel"}:
            if purpose is not UrlPurpose.NAVIGATION:
                raise _url_error(f"{scheme}: URLs are only allowed for navigation", purpose)
        elif scheme in {"http", "https"}:
            if not allow_external:
                raise _url_error("External HTTP(S) URLs require allow_external=True", purpose)
            if not parts.netloc:
                raise _url_error("HTTP(S) URL requires a host", purpose)
        elif scheme == "":
            if raw.startswith("//") or scanned.startswith("//"):
                raise _url_error(
                    "Protocol-relative URLs require an explicit absolute scheme",
                    purpose,
                )
            # Reject encoded absolute schemes that urlsplit treated as relative.
            if scanned_scheme and scanned_scheme not in {"", "mailto", "tel", "http", "https"}:
                raise _url_error(f"Unsupported or encoded URL scheme {scanned_scheme!r}", purpose)
            if scanned_scheme in {"http", "https"} and not allow_external:
                raise _url_error("External HTTP(S) URLs require allow_external=True", purpose)
        else:
            raise _url_error(f"Unsupported URL scheme {scheme!r}", purpose)

        if parts.username is not None or parts.password is not None:
            raise _url_error("URLs must not contain credentials", purpose)

        obj = object.__new__(cls)
        object.__setattr__(obj, "_value", raw)
        object.__setattr__(obj, "_purpose", purpose)
        object.__setattr__(obj, "_allow_external", allow_external)
        return obj

    @property
    def value(self) -> str:
        return self._value  # type: ignore[attr-defined]

    @property
    def purpose(self) -> UrlPurpose:
        return self._purpose  # type: ignore[attr-defined]

    def __str__(self) -> str:
        return self.value

    def __repr__(self) -> str:
        return f"SafeUrl(purpose={self.purpose.value!r})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, SafeUrl):
            return NotImplemented
        return self.value == other.value and self.purpose is other.purpose

    def __hash__(self) -> int:
        return hash(("SafeUrl", self.value, self.purpose))


def _url_error(message: str, purpose: UrlPurpose) -> HedronError:
    return error(
        "HED-SEC-0001",
        title="Unsafe or invalid URL",
        explanation=message,
        remediation=(
            "Provide a relative same-origin URL or an explicitly allowed "
            f"scheme for purpose={purpose.value}."
        ),
        context={"purpose": purpose.value},
    )


def is_secret(value: Any) -> bool:
    return isinstance(value, Secret)


def redact_value(value: Any) -> Any:
    if isinstance(value, Secret):
        return _REDACTED
    if isinstance(value, list):
        return [redact_value(v) for v in value]
    if isinstance(value, tuple):
        return tuple(redact_value(v) for v in value)
    if isinstance(value, dict):
        return {k: redact_value(v) for k, v in value.items()}
    return value

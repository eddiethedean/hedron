"""Security boundary types: Secret, TrustedHtml, SafeUrl."""

from __future__ import annotations

import html as html_stdlib
import re
from enum import StrEnum
from typing import Any, Generic, TypeVar, get_args, get_origin
from urllib.parse import unquote, urlsplit

from pydantic import GetCoreSchemaHandler, TypeAdapter
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


def _validate_secret_inner(source_type: Any, value: Any) -> Any:
    args = get_args(source_type)
    if not args:
        return value
    inner = args[0]
    origin = get_origin(inner) or inner
    if origin is Any:
        return value
    try:
        return TypeAdapter(inner).validate_python(value)
    except Exception as exc:  # noqa: BLE001
        raise error(
            "HED-SEC-0010",
            title="Secret value type mismatch",
            explanation=f"Secret expected {inner!r}, got {type(value).__name__}.",
            remediation="Pass a value matching the Secret[T] type parameter.",
        ) from exc


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

    def __getstate__(self) -> dict[str, object]:
        return {"value": _REDACTED}

    def __setattr__(self, name: str, value: Any) -> None:
        raise AttributeError("Secret is immutable")

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        def validate(value: Any) -> Secret[Any]:
            if isinstance(value, Secret):
                inner = _validate_secret_inner(source_type, value.reveal())
                return Secret(inner)
            inner = _validate_secret_inner(source_type, value)
            return Secret(inner)

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

    @classmethod
    def nh3(cls, value: str, *, tags: set[str] | None = None) -> TrustedHtml:
        """Sanitize HTML with nh3 and record policy provenance.

        Requires the optional ``nh3`` dependency (``pip install "hedron[sanitize]"``
        or ``pip install "hedron[markdown]"``).
        """
        if not isinstance(value, str):
            raise TypeError("TrustedHtml value must be a string")
        try:
            import nh3
        except ImportError as exc:  # pragma: no cover - exercised when extra missing
            raise error(
                "HED-SEC-0020",
                title="nh3 sanitizer not installed",
                explanation="TrustedHtml.nh3 requires the nh3 package.",
                remediation='Install with: pip install "hedron[sanitize]" or pip install nh3',
            ) from exc
        cleaned = nh3.clean(value, tags=tags) if tags is not None else nh3.clean(value)
        version = getattr(nh3, "__version__", "unknown")
        return cls.reviewed(cleaned, source=f"nh3:{version}")

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
# Unicode format/bidi/ZWSP/BOM and other Cf chars used to smuggle schemes.
_FORMAT_CHARS = re.compile(
    r"[\u200b-\u200f\u202a-\u202e\u2060-\u2064\u2066-\u2069\ufeff\u00ad\u180e]"
)
_SCHEME_PREFIX = re.compile(r"^([a-z][a-z0-9+.-]*):", re.IGNORECASE)


def _strip_format_chars(value: str) -> str:
    return _FORMAT_CHARS.sub("", value)


def _normalize_for_scheme_scan(value: str) -> str:
    """HTML-unescape and percent-decode (bounded) to defeat scheme smuggling."""
    current = _strip_format_chars(value)
    for _ in range(_DECODE_ROUNDS):
        unescaped = html_stdlib.unescape(current)
        try:
            decoded = unquote(unescaped, errors="strict")
        except Exception:
            decoded = unquote(unescaped)
        # Collapse whitespace used to break scheme detection; drop format chars each round.
        collapsed = _strip_format_chars(re.sub(r"\s+", "", decoded))
        if collapsed == current:
            break
        current = collapsed
    return current.lower()


def contains_dangerous_scheme(value: str) -> bool:
    """True when value smuggles a dangerous URL scheme (for SVG/icon scans)."""
    scanned = _normalize_for_scheme_scan(value)
    scheme = _extract_scheme(scanned)
    if scheme in _DANGEROUS_SCHEMES:
        return True
    return any(f"{dangerous}:" in scanned for dangerous in _DANGEROUS_SCHEMES)


def _extract_scheme(value: str) -> str:
    match = _SCHEME_PREFIX.match(value)
    return match.group(1).lower() if match else ""


def _purpose_for_attr(attr: str) -> UrlPurpose:
    lower = attr.lower()
    if lower in {"action", "formaction"}:
        return UrlPurpose.FORM_ACTION
    if lower in {"src", "poster", "srcset", "ping"} or lower.endswith("src"):
        return UrlPurpose.ASSET
    if lower in {
        "hx-get",
        "hx-post",
        "hx-put",
        "hx-patch",
        "hx-delete",
        "hx-push-url",
        "hx-replace-url",
    }:
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

        if _FORMAT_CHARS.search(raw):
            raise _url_error("URL contains disallowed Unicode format characters", purpose)

        scanned = _normalize_for_scheme_scan(raw)
        if _CONTROL_CHARS.search(scanned):
            raise _url_error("URL contains control characters after decoding", purpose)
        if _FORMAT_CHARS.search(scanned):
            raise _url_error("URL contains disallowed Unicode format characters", purpose)

        scanned_scheme = _extract_scheme(scanned)
        if scanned_scheme in _DANGEROUS_SCHEMES:
            raise _url_error(f"Disallowed URL scheme for {purpose.value}", purpose)

        # Reject dangerous schemes only when they appear as a leading scheme token
        # (not as an incidental substring in paths like /api/data:export).
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

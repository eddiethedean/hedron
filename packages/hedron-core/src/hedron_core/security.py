"""Security boundary types: Secret, TrustedHtml, SafeUrl."""

from __future__ import annotations

import re
from enum import StrEnum
from typing import Any, TypeVar
from urllib.parse import urlsplit

from hedron_core.diagnostics import HedronError, error

T = TypeVar("T")

_REDACTED = "***"


class UrlPurpose(StrEnum):
    NAVIGATION = "navigation"
    ASSET = "asset"
    FORM_ACTION = "form_action"
    REDIRECT = "redirect"


class Secret[T]:
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

        # Block scheme smuggling via whitespace / mixed case before parse.
        lowered = raw.lower()
        for scheme in _DANGEROUS_SCHEMES:
            if lowered.startswith(f"{scheme}:"):
                raise _url_error(f"Disallowed URL scheme for {purpose.value}", purpose)

        parts = urlsplit(raw)
        scheme = parts.scheme.lower()

        if scheme in _DANGEROUS_SCHEMES:
            raise _url_error(f"Disallowed URL scheme for {purpose.value}", purpose)

        if "\\" in raw or "\n" in raw or "\r" in raw:
            raise _url_error("URL contains disallowed characters", purpose)

        if scheme in {"mailto", "tel"}:
            if purpose is not UrlPurpose.NAVIGATION:
                raise _url_error(f"{scheme}: URLs are only allowed for navigation", purpose)
        elif scheme in {"http", "https"}:
            if not allow_external:
                raise _url_error("External HTTP(S) URLs require allow_external=True", purpose)
            if not parts.netloc:
                raise _url_error("HTTP(S) URL requires a host", purpose)
        elif scheme == "":
            # Relative / same-origin path or fragment.
            if raw.startswith("//"):
                raise _url_error(
                    "Protocol-relative URLs require an explicit absolute scheme",
                    purpose,
                )
            if purpose is UrlPurpose.REDIRECT and raw.startswith("//"):
                raise _url_error("Open redirect via protocol-relative URL", purpose)
        else:
            raise _url_error(f"Unsupported URL scheme {scheme!r}", purpose)

        # Credential-bearing absolute URLs are rejected.
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
    return value

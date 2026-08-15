"""Pluggable CSRF strategy protocol and built-in strategies (phase 0.22)."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from hedron_core.csrf import generate_csrf_token, tokens_match, validate_double_submit

__all__ = [
    "DEFAULT_CSRF_COOKIE_NAME",
    "DEFAULT_CSRF_FORM_FIELD",
    "DEFAULT_CSRF_HEADER_NAME",
    "CsrfStrategy",
    "CsrfTokenProvider",
    "CsrfValidationError",
    "DoubleSubmitCookieCsrf",
    "SessionTokenCsrf",
]

DEFAULT_CSRF_COOKIE_NAME = "hedron_csrf"
DEFAULT_CSRF_HEADER_NAME = "X-CSRF-Token"
DEFAULT_CSRF_FORM_FIELD = "csrf_token"


class CsrfValidationError(Exception):
    """Raised by strategies when CSRF validation fails (hosts map to HTTP 403)."""


@runtime_checkable
class CsrfTokenProvider(Protocol):
    """Issued CSRF material for widgets (``RenderContext`` structurally matches)."""

    @property
    def csrf_token(self) -> str | None: ...

    @property
    def csrf_form_field(self) -> str: ...


def resolve_csrf_field_values(
    *,
    token: str | None,
    name: str | None,
    provider: CsrfTokenProvider | None,
) -> tuple[str, str]:
    """Resolve hidden-input token/name from explicit values or a token provider.

    Returns:
        ``(token, field_name)``.

    Raises:
        ValueError: When no token is available from props or the provider.
    """
    resolved_token = token
    if resolved_token is None and provider is not None:
        resolved_token = provider.csrf_token
    resolved_name = name
    if resolved_name is None:
        if provider is not None:
            resolved_name = provider.csrf_form_field
        else:
            resolved_name = DEFAULT_CSRF_FORM_FIELD
    if not resolved_token:
        raise ValueError(
            "CsrfField requires token= or a RenderContext with csrf_token "
            "(FastAPI pages populate this automatically when CSRF is enabled)"
        )
    return resolved_token, resolved_name


@runtime_checkable
class CsrfStrategy(Protocol):
    """Validate and optionally issue CSRF material for unsafe requests.

    Cookie, header, and form-field names live on the strategy. Hosts must read
    names from the resolved strategy rather than duplicating them beside it.
    """

    # Properties (not bare attrs) so frozen strategy dataclasses structurally match.
    @property
    def form_field(self) -> str: ...

    @property
    def header_name(self) -> str: ...

    @property
    def cookie_name(self) -> str: ...

    def issue(self, request: object) -> str:
        """Return the token value to embed (cookie seed and/or form field)."""
        ...

    def validate(
        self,
        request: object,
        *,
        form_value: str | None,
        header_value: str | None,
    ) -> None:
        """Accept form field or header; raise CsrfValidationError on failure."""
        ...


def _cookie_get(request: object, name: str) -> str | None:
    cookies = getattr(request, "cookies", None)
    if cookies is None:
        return None
    value = cookies.get(name)
    return value if isinstance(value, str) and value else None


def _state_get(request: object, attr: str) -> str | None:
    state = getattr(request, "state", None)
    if state is None:
        return None
    value = getattr(state, attr, None)
    return value if isinstance(value, str) and value else None


def _state_set(request: object, attr: str, value: str) -> None:
    state = getattr(request, "state", None)
    if state is not None:
        setattr(state, attr, value)


@dataclass(frozen=True, slots=True)
class DoubleSubmitCookieCsrf:
    """Cookie double-submit strategy (default for named security profiles)."""

    cookie_name: str = DEFAULT_CSRF_COOKIE_NAME
    form_field: str = DEFAULT_CSRF_FORM_FIELD
    header_name: str = DEFAULT_CSRF_HEADER_NAME
    sets_cookie: bool = True

    def issue(self, request: object) -> str:
        existing = _cookie_get(request, self.cookie_name)
        if existing:
            _state_set(request, "hedron_csrf_token", existing)
            return existing
        cached = _state_get(request, "hedron_csrf_token")
        if cached:
            return cached
        value = generate_csrf_token()
        _state_set(request, "hedron_csrf_token", value)
        return value

    def validate(
        self,
        request: object,
        *,
        form_value: str | None,
        header_value: str | None,
    ) -> None:
        cookie = _cookie_get(request, self.cookie_name)
        if not validate_double_submit(
            cookie_token=cookie,
            form_token=form_value,
            header_token=header_value,
        ):
            raise CsrfValidationError("CSRF validation failed")


@dataclass(frozen=True, slots=True)
class SessionTokenCsrf:
    """App-owned synchronizer token (no Starlette cookie session required)."""

    get_expected: Callable[[object], str | None]
    form_field: str = DEFAULT_CSRF_FORM_FIELD
    header_name: str = DEFAULT_CSRF_HEADER_NAME
    sets_cookie: bool = False
    cookie_name: str = ""

    def issue(self, request: object) -> str:
        # Missing tokens must not 500 safe GET/page renders; validate() rejects POSTs.
        expected = self.get_expected(request)
        if isinstance(expected, str) and expected:
            _state_set(request, "hedron_csrf_token", expected)
            return expected
        return ""

    def validate(
        self,
        request: object,
        *,
        form_value: str | None,
        header_value: str | None,
    ) -> None:
        expected = self.get_expected(request)
        # Match validate_double_submit precedence: form field, then header.
        provided = form_value or header_value
        if not isinstance(expected, str) or not expected:
            raise CsrfValidationError("CSRF validation failed")
        if not isinstance(provided, str) or not tokens_match(expected, provided):
            raise CsrfValidationError("CSRF validation failed")

"""Purpose-specific trust-boundary compiler (SINK-056)."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any

from hedron_core.active_markup import has_active_markup
from hedron_core.htmx_contract import safe_css_selector
from hedron_core.security.trusted import TrustedHtml
from hedron_core.security.urls import SafeUrl, UrlPurpose, contains_dangerous_scheme


class TrustPurpose(StrEnum):
    URL_NAVIGATION = "url.navigation"
    URL_ASSET = "url.asset"
    URL_FORM_ACTION = "url.form_action"
    URL_REDIRECT = "url.redirect"
    SELECTOR = "selector"
    MARKUP_HTML = "markup.html"
    MARKUP_SVG = "markup.svg"
    BROWSER_PAYLOAD = "browser.payload"


class TrustCompileError(ValueError):
    """Raised when a value cannot be compiled for the requested purpose."""


@dataclass(frozen=True, slots=True)
class CompiledTrust:
    """Opaque compiled trust value that cannot be reused across purposes."""

    purpose: TrustPurpose
    value: str
    source: str = "compiled"

    def as_str(self) -> str:
        return self.value


_PURPOSE_TO_URL: dict[TrustPurpose, UrlPurpose] = {
    TrustPurpose.URL_NAVIGATION: UrlPurpose.NAVIGATION,
    TrustPurpose.URL_ASSET: UrlPurpose.ASSET,
    TrustPurpose.URL_FORM_ACTION: UrlPurpose.FORM_ACTION,
    TrustPurpose.URL_REDIRECT: UrlPurpose.REDIRECT,
}


def compile_trust(
    value: Any,
    purpose: TrustPurpose | str,
    *,
    source: str = "application",
) -> CompiledTrust:
    """Compile a value for a single purpose; cross-purpose reuse fails closed."""
    purpose_enum = purpose if isinstance(purpose, TrustPurpose) else TrustPurpose(str(purpose))
    if isinstance(value, CompiledTrust):
        if value.purpose is not purpose_enum:
            raise TrustCompileError(
                f"cross-purpose reuse denied: {value.purpose.value} as {purpose_enum.value}"
            )
        return value
    text = value if isinstance(value, str) else str(value)
    if purpose_enum in _PURPOSE_TO_URL:
        try:
            url = SafeUrl.parse(text, purpose=_PURPOSE_TO_URL[purpose_enum])
        except Exception as exc:
            raise TrustCompileError(str(exc)) from exc
        return CompiledTrust(purpose=purpose_enum, value=str(url), source=source)
    if purpose_enum is TrustPurpose.SELECTOR:
        if not safe_css_selector(text):
            raise TrustCompileError("unsafe CSS selector")
        return CompiledTrust(purpose=purpose_enum, value=text, source=source)
    if purpose_enum is TrustPurpose.MARKUP_HTML:
        if isinstance(value, TrustedHtml):
            return CompiledTrust(purpose=purpose_enum, value=str(value), source=source)
        trusted = TrustedHtml.reviewed(text, source=source)
        return CompiledTrust(purpose=purpose_enum, value=str(trusted), source=source)
    if purpose_enum is TrustPurpose.MARKUP_SVG:
        if has_active_markup(text):
            raise TrustCompileError("active markup in SVG")
        if contains_dangerous_scheme(text):
            raise TrustCompileError("dangerous scheme in SVG markup")
        return CompiledTrust(purpose=purpose_enum, value=text, source=source)
    if purpose_enum is TrustPurpose.BROWSER_PAYLOAD:
        if contains_dangerous_scheme(text) or "<script" in text.lower():
            raise TrustCompileError("dangerous browser payload")
        return CompiledTrust(purpose=purpose_enum, value=text, source=source)
    raise TrustCompileError(f"unsupported trust purpose: {purpose_enum}")

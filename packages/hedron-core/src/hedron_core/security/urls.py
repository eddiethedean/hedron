"""Validated URLs and purpose checks."""

from __future__ import annotations

import html as html_stdlib
import posixpath
import re
import unicodedata
from enum import StrEnum
from urllib.parse import unquote, urlsplit

from hedron_core.diagnostics import HedronError, error

_DECODE_ROUNDS = 3


class UrlPurpose(StrEnum):
    NAVIGATION = "navigation"
    ASSET = "asset"
    FORM_ACTION = "form_action"
    REDIRECT = "redirect"


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


def nfkc_strip_format(value: str) -> str:
    """NFKC-normalize and drop Unicode format (Cf) characters.

    Shared by SafeUrl / ``contains_dangerous_scheme`` scans and EVAL-020 so
    fullwidth schemes such as ``ｊａｖａｓｃｒｉｐｔ:`` fold to ASCII.
    """
    return "".join(
        ch for ch in unicodedata.normalize("NFKC", value) if unicodedata.category(ch) != "Cf"
    )


def _normalize_for_scheme_scan(value: str) -> str:
    """HTML-unescape, percent-decode, and NFKC-normalize to defeat scheme smuggling."""
    current = nfkc_strip_format(value)
    for _ in range(_DECODE_ROUNDS):
        unescaped = html_stdlib.unescape(current)
        try:
            decoded = unquote(unescaped, errors="strict")
        except Exception:  # noqa: BLE001
            decoded = unquote(unescaped)
        # Collapse whitespace used to break scheme detection; drop format chars each round.
        collapsed = nfkc_strip_format(re.sub(r"\s+", "", decoded))
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


def reject_asset_path_traversal(raw: str, *, purpose: UrlPurpose = UrlPurpose.ASSET) -> None:
    """Reject literal or percent-encoded ``..`` segments in root-relative paths."""
    path_only = raw.split("?", 1)[0].split("#", 1)[0]
    cleaned = path_only if path_only.startswith("/") else f"/{path_only.lstrip('/')}"
    decoded = _normalize_for_scheme_scan(path_only)
    decoded_path = decoded if decoded.startswith("/") else f"/{decoded.lstrip('/')}"
    normalized = posixpath.normpath(decoded_path)
    cleaned_norm = posixpath.normpath(cleaned)
    segments = decoded_path.split("/")
    if (
        normalized != decoded_path
        or cleaned_norm != cleaned
        or any(seg == ".." or ".." in seg for seg in segments)
        or any(seg == ".." or ".." in seg for seg in cleaned.split("/"))
    ):
        label = "Asset path" if purpose is UrlPurpose.ASSET else "Relative URL path"
        raise _url_error(
            f"{label} must be normalized without '..' (got {raw!r}, normalized={normalized!r})",
            purpose,
        )


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
    _value: str
    _purpose: UrlPurpose
    _allow_external: bool

    def __init__(self, *args: object, **kwargs: object) -> None:
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
            # Form/nav/redirect same-origin URLs must be root-relative, or a
            # same-document fragment for navigation (`#id`).
            if purpose in {
                UrlPurpose.NAVIGATION,
                UrlPurpose.FORM_ACTION,
                UrlPurpose.REDIRECT,
            }:
                ok_root = raw.startswith("/") and not raw.startswith("//")
                ok_fragment = purpose is UrlPurpose.NAVIGATION and raw.startswith("#")
                if not (ok_root or ok_fragment):
                    raise _url_error(
                        "Relative URLs for navigation/form/redirect must be root-relative "
                        "(start with /) or a same-document fragment (#…) for navigation",
                        purpose,
                    )
        else:
            raise _url_error(f"Unsupported URL scheme {scheme!r}", purpose)

        if parts.username is not None or parts.password is not None:
            raise _url_error("URLs must not contain credentials", purpose)

        if purpose is UrlPurpose.ASSET and scheme == "":
            # Same-origin relative assets: always reject encoded path traversal.
            # allow_external only gates absolute http(s), never traversal.
            reject_asset_path_traversal(raw, purpose=purpose)
        elif (
            purpose
            in {
                UrlPurpose.NAVIGATION,
                UrlPurpose.FORM_ACTION,
                UrlPurpose.REDIRECT,
            }
            and scheme == ""
            and (
                raw.startswith("/") or raw.startswith("./") or raw.startswith("../") or ".." in raw
            )
        ):
            reject_asset_path_traversal(raw, purpose=purpose)

        obj = object.__new__(cls)
        object.__setattr__(obj, "_value", raw)
        object.__setattr__(obj, "_purpose", purpose)
        object.__setattr__(obj, "_allow_external", allow_external)
        return obj

    @property
    def value(self) -> str:
        return self._value

    @property
    def purpose(self) -> UrlPurpose:
        return self._purpose

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

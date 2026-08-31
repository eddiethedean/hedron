"""Redact session/project IDs and token-like values before logs or JSON."""

from __future__ import annotations

import re
from collections.abc import Mapping
from typing import Any, cast
from urllib.parse import unquote_plus, urlsplit, urlunsplit

_SENSITIVE_QUERY_KEYS = frozenset(
    {
        "token",
        "code",
        "session",
        "password",
        "secret",
        "access_token",
        "refresh_token",
        "api_key",
        "license",
    }
)
_TOKENISH_PATH = re.compile(r"(^|/)([a-f0-9]{16,}|[A-Za-z0-9_-]{20,})(/|$)", re.IGNORECASE)
_LICENSE_SHAPE = re.compile(r"\b[A-Z0-9]{4}(?:-[A-Z0-9]{4}){5,}\b", re.IGNORECASE)
_URL_CREDENTIALS = re.compile(r"(?i)(https?://)([^/\s@]+)@")
_SENSITIVE_ASSIGNMENT = re.compile(
    r"(?i)\b(token|code|session|password|secret|access_token|refresh_token|api_key|license|authorization|credential|cookie)"
    r"\s*=\s*([^&\s]+)"
)
_SENSITIVE_HEADER = re.compile(
    r"(?im)(\b(?:authorization|proxy-authorization|cookie|set-cookie|"
    r"rstudio-connect-credentials|rstudio-connect-user-session|"
    r"x-(?:csrf|xsrf)-token)\s*:\s*)[^\r\n]*"
)
_SENSITIVE_KEY = re.compile(
    r"(?i)(token|secret|password|passwd|credential|authorization|cookie(?![_-]?(mount|path|name))|license|api[_-]?key|private[_-]?key)"
)
_REDACTED = "***"


def _redact_nested(value: object) -> object:
    if isinstance(value, str):
        return redact_text(value)
    if isinstance(value, list):
        return [_redact_nested(item) for item in cast(list[object], value)]
    if isinstance(value, tuple):
        return tuple(_redact_nested(item) for item in cast(tuple[object, ...], value))
    if isinstance(value, dict):
        mapping = cast(dict[object, object], value)
        redacted: dict[object, object] = {}
        for key, item in mapping.items():
            key_text = str(key).lower()
            redacted[key] = (
                _REDACTED
                if (key_text in _SENSITIVE_QUERY_KEYS or _SENSITIVE_KEY.search(key_text))
                else _redact_nested(item)
            )
        return redacted
    return value


def redact_path(path: str) -> str:
    redacted = _TOKENISH_PATH.sub(r"\1***\3", path or "")
    return _LICENSE_SHAPE.sub(_REDACTED, redacted)


def redact_query(query: str) -> str:
    if not query:
        return ""
    parts: list[str] = []
    for piece in query.split("&"):
        key, _, _value = piece.partition("=")
        lowered = unquote_plus(key).lower()
        if lowered in _SENSITIVE_QUERY_KEYS or "token" in lowered or "license" in lowered:
            parts.append(f"{key}={_REDACTED}")
        else:
            parts.append(piece)
    return "&".join(parts)


def redact_url(url: str) -> str:
    raw = (url or "").strip()
    if not raw:
        return raw
    parts = urlsplit(raw)
    netloc = parts.netloc.rsplit("@", 1)[-1] if "@" in parts.netloc else parts.netloc
    return urlunsplit(
        (parts.scheme, netloc, redact_path(parts.path), redact_query(parts.query), "")
    )


def redact_text(value: str) -> str:
    redacted = _URL_CREDENTIALS.sub(r"\1***@", value or "")
    redacted = _SENSITIVE_HEADER.sub(r"\1***", redacted)
    redacted = _SENSITIVE_ASSIGNMENT.sub(r"\1=***", redacted)
    return _LICENSE_SHAPE.sub(_REDACTED, redact_path(redacted))


def redact_scope_for_log(scope: Mapping[str, Any]) -> dict[str, Any]:
    path = redact_path(str(scope.get("path") or ""))
    raw = scope.get("raw_path")
    raw_display: str | bytes
    if isinstance(raw, bytes):
        raw_display = redact_path(raw.decode(errors="replace")).encode()
    else:
        raw_display = redact_path(str(raw or ""))
    qs_raw = scope.get("query_string") or b""
    qs = qs_raw.decode(errors="replace") if isinstance(qs_raw, bytes) else str(qs_raw)
    return {
        "method": scope.get("method"),
        "root_path": redact_path(str(scope.get("root_path") or "")),
        "path": path,
        "raw_path": raw_display,
        "query_string": redact_query(qs),
    }


def redact_record(data: Mapping[str, object]) -> dict[str, object]:
    redacted = _redact_nested(dict(data))
    if not isinstance(redacted, dict):
        return {str(key): value for key, value in data.items()}
    typed = cast(dict[object, object], redacted)
    payload: dict[str, object] = {str(key): value for key, value in typed.items()}
    for key in ("browser_mount", "cookie_mount", "source", "bind"):
        value = payload.get(key)
        if isinstance(value, str):
            payload[key] = redact_text(value)
    external_origin = payload.get("external_origin")
    if isinstance(external_origin, str):
        payload["external_origin"] = redact_url(external_origin)
    warnings = payload.get("warnings")
    if isinstance(warnings, list):
        warning_values = cast(list[object], warnings)
        payload["warnings"] = [redact_text(str(item)) for item in warning_values]
    return payload

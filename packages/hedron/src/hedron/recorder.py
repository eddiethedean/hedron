"""Interaction/API recorder (RFC-0048 / RECORD-018).

Emits redacted, reviewable Python and HTTP examples only for explicitly public
endpoints. Snippets never expand endpoint authority or record credentials.
"""

from __future__ import annotations

import json
import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any, cast

__all__ = [
    "RecordedExchange",
    "RecordingSnippet",
    "InteractionRecorder",
    "SENSITIVE_HEADER_NAMES",
    "SENSITIVE_FIELD_NAMES",
]

SENSITIVE_HEADER_NAMES = frozenset(
    {
        "authorization",
        "cookie",
        "set-cookie",
        "x-api-key",
        "x-auth-token",
        "proxy-authorization",
    }
)

SENSITIVE_FIELD_NAMES = frozenset(
    {
        "password",
        "secret",
        "token",
        "api_key",
        "apikey",
        "access_token",
        "refresh_token",
        "session",
        "csrf",
        "credential",
    }
)

_REDACTED = "[redacted]"


def _canonical_key(key: str) -> str:
    return key.casefold().replace("-", "_")


_SENSITIVE_KEYS = frozenset(
    _canonical_key(name) for name in SENSITIVE_FIELD_NAMES | SENSITIVE_HEADER_NAMES
)


def _is_sensitive_key(key: str) -> bool:
    lowered = _canonical_key(key)
    if lowered in _SENSITIVE_KEYS:
        return True
    return any(part in lowered for part in ("password", "secret", "token", "credential"))


def _redact_value(value: Any) -> Any:
    if isinstance(value, Mapping):
        return _redact_mapping(cast(Mapping[str, Any], value))
    if isinstance(value, list):
        return [_redact_value(item) for item in cast(list[Any], value)]
    if isinstance(value, tuple):
        return tuple(_redact_value(item) for item in cast(tuple[Any, ...], value))
    return value


def _redact_mapping(data: Mapping[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key, value in data.items():
        if _is_sensitive_key(str(key)):
            out[str(key)] = _REDACTED
        else:
            out[str(key)] = _redact_value(value)
    return out


@dataclass(frozen=True, slots=True)
class RecordedExchange:
    method: str
    path: str
    public: bool
    headers: Mapping[str, str] = field(default_factory=dict[str, str])
    body: Mapping[str, Any] | None = None
    session_assumptions: tuple[str, ...] = ()
    file_fixtures: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class RecordingSnippet:
    language: str  # "python" | "http"
    content: str
    endpoint: str
    warnings: tuple[str, ...] = ()


@dataclass
class InteractionRecorder:
    """Record public endpoint exchanges into redacted client snippets."""

    public_endpoints: set[str] = field(default_factory=set[str])
    _exchanges: list[RecordedExchange] = field(default_factory=list[RecordedExchange], init=False)

    def declare_public(self, *endpoints: str) -> None:
        """Declare paths that may be recorded (method:path or path-only)."""
        self.public_endpoints.update(endpoints)

    def _is_public(self, method: str, path: str) -> bool:
        key = f"{method.upper()}:{path}"
        return key in self.public_endpoints or path in self.public_endpoints

    def record(
        self,
        *,
        method: str,
        path: str,
        headers: Mapping[str, str] | None = None,
        body: Mapping[str, Any] | None = None,
        session_assumptions: Sequence[str] = (),
        file_fixtures: Sequence[str] = (),
        public: bool | None = None,
    ) -> RecordedExchange | None:
        allowlisted = self._is_public(method, path)
        # ``public=`` can only opt out of an allowlisted path; it cannot force-record.
        if not allowlisted or public is False:
            return None
        redacted_headers = {
            k: (_REDACTED if _is_sensitive_key(k) else v) for k, v in dict(headers or {}).items()
        }
        redacted_body = _redact_mapping(body) if body is not None else None
        exchange = RecordedExchange(
            method=method.upper(),
            path=path,
            public=True,
            headers=redacted_headers,
            body=redacted_body,
            session_assumptions=tuple(session_assumptions),
            file_fixtures=tuple(file_fixtures),
        )
        self._exchanges.append(exchange)
        return exchange

    def snippets(self) -> list[RecordingSnippet]:
        out: list[RecordingSnippet] = []
        for exchange in self._exchanges:
            warnings: list[str] = []
            if exchange.session_assumptions:
                warnings.append(
                    "Requires session assumptions: " + ", ".join(exchange.session_assumptions)
                )
            if exchange.file_fixtures:
                warnings.append("File fixtures: " + ", ".join(exchange.file_fixtures))
            warnings.append("Snippet does not expand endpoint authority.")
            http_lines = [f"{exchange.method} {exchange.path} HTTP/1.1"]
            for key, value in exchange.headers.items():
                http_lines.append(f"{key}: {value}")
            if exchange.body is not None:
                http_lines.append("")
                http_lines.append(json.dumps(exchange.body, indent=2, sort_keys=True))
            out.append(
                RecordingSnippet(
                    language="http",
                    content="\n".join(http_lines),
                    endpoint=f"{exchange.method} {exchange.path}",
                    warnings=tuple(warnings),
                )
            )
            body_repr = (
                json.dumps(exchange.body, indent=4, sort_keys=True)
                if exchange.body is not None
                else "None"
            )
            # Never inject credentials into generated Python.
            py = (
                "import httpx\n\n"
                f"# Public endpoint only — authority is not expanded by this recorder.\n"
                f"response = httpx.request(\n"
                f"    {exchange.method!r},\n"
                f"    {exchange.path!r},\n"
                f"    json={body_repr},\n"
                f")\n"
                f"print(response.status_code)\n"
            )
            # Guard: generated snippet must not contain literal secrets.
            if re.search(r"(?i)(bearer\s+[a-z0-9._\-]+|password\s*=\s*['\"][^'\"]+)", py):
                raise ValueError("Recorder refused to emit credential-bearing snippet")
            out.append(
                RecordingSnippet(
                    language="python",
                    content=py,
                    endpoint=f"{exchange.method} {exchange.path}",
                    warnings=tuple(warnings),
                )
            )
        return out

    @property
    def exchanges(self) -> tuple[RecordedExchange, ...]:
        return tuple(self._exchanges)

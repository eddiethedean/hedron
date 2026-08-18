"""Bounded browser-local draft transfer envelope (STATE-041).

Canonical sessionStorage contract (shared with ``composition-041.mjs``):

- key: ``hedron:draft:v1:`` + ``encodeURIComponent`` of app, route family,
  element contract, schema version, and subject, joined by ``:``
- JSON: camelCase field names; ``createdAt`` / ``expiresAt`` in milliseconds
"""

from __future__ import annotations

import json
import time
from collections.abc import Mapping
from dataclasses import dataclass
from hashlib import sha256
from typing import Any
from urllib.parse import quote

FORBIDDEN_FIELD_TOKENS = frozenset(
    {"auth", "authorization", "cookie", "csrf", "file", "html", "password", "secret", "token"}
)
MAX_ENTRY_BYTES = 32_768
MAX_TTL_SECONDS = 1800
MAX_TTL_MS = MAX_TTL_SECONDS * 1000
# Match JS encodeURIComponent unescaped set: A-Z a-z 0-9 - _ . ! ~ * ' ( )
_URI_COMPONENT_SAFE = "-_.!~*'()"


def subject_fingerprint(subject: str, authority_revision: str) -> str:
    if not subject or not authority_revision:
        raise ValueError("subject and authority revision are required")
    return sha256(f"{subject}\0{authority_revision}".encode()).hexdigest()[:24]


def draft_storage_key(
    *,
    app: str,
    route_family: str,
    element_contract: str,
    schema_version: str,
    subject: str,
) -> str:
    """Return the canonical sessionStorage key used by the browser module."""
    parts = (app, route_family, element_contract, schema_version, subject)
    encoded = ":".join(quote(part, safe=_URI_COMPONENT_SAFE) for part in parts)
    return f"hedron:draft:v1:{encoded}"


@dataclass(frozen=True, slots=True)
class DraftTransferEnvelope:
    app: str
    route_family: str
    element_contract: str
    schema_version: str
    subject: str
    fields: Mapping[str, Any]
    created_at: int
    expires_at: int
    operation_id: str

    @classmethod
    def create(
        cls,
        *,
        app: str,
        route_family: str,
        element_contract: str,
        schema_version: str,
        subject: str,
        fields: Mapping[str, Any],
        operation_id: str,
        ttl_seconds: int = 300,
        now: int | None = None,
    ) -> DraftTransferEnvelope:
        """Mint an envelope. ``now`` is milliseconds (JS ``Date.now()``)."""
        if not 1 <= ttl_seconds <= MAX_TTL_SECONDS:
            raise ValueError("draft TTL is outside the allowed range")
        timestamp = int(time.time() * 1000) if now is None else int(now)
        envelope = cls(
            app=app,
            route_family=route_family,
            element_contract=element_contract,
            schema_version=schema_version,
            subject=subject,
            fields=dict(fields),
            created_at=timestamp,
            expires_at=timestamp + ttl_seconds * 1000,
            operation_id=operation_id,
        )
        envelope.validate(now=timestamp)
        return envelope

    @classmethod
    def from_json(cls, raw: str, *, now: int | None = None) -> DraftTransferEnvelope:
        """Parse a canonical camelCase millisecond envelope from the browser module."""
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ValueError("invalid draft transfer JSON") from exc
        if not isinstance(data, dict) or data.get("version") != 1:
            raise ValueError("unsupported draft transfer version")
        fields = data.get("fields")
        if not isinstance(fields, dict):
            raise ValueError("draft transfer fields must be an object")
        try:
            envelope = cls(
                app=str(data["app"]),
                route_family=str(data["routeFamily"]),
                element_contract=str(data["elementContract"]),
                schema_version=str(data["schemaVersion"]),
                subject=str(data["subject"]),
                fields=fields,
                created_at=int(data["createdAt"]),
                expires_at=int(data["expiresAt"]),
                operation_id=str(data["operationId"]),
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError("draft transfer envelope is missing required fields") from exc
        envelope.validate(now=now)
        return envelope

    @property
    def storage_key(self) -> str:
        return draft_storage_key(
            app=self.app,
            route_family=self.route_family,
            element_contract=self.element_contract,
            schema_version=self.schema_version,
            subject=self.subject,
        )

    def validate(self, *, now: int | None = None) -> None:
        required = (
            self.app,
            self.route_family,
            self.element_contract,
            self.schema_version,
            self.subject,
            self.operation_id,
        )
        if not all(isinstance(value, str) and value for value in required):
            raise ValueError("draft transfer identity fields must be non-empty strings")
        timestamp = int(time.time() * 1000) if now is None else int(now)
        if self.expires_at <= timestamp or self.expires_at - self.created_at > MAX_TTL_MS:
            raise ValueError("draft transfer is expired or exceeds maximum TTL")
        for name, value in self.fields.items():
            lowered = str(name).lower()
            if lowered in FORBIDDEN_FIELD_TOKENS:
                raise ValueError(f"forbidden draft field: {name!r}")
            if isinstance(value, (bytes, bytearray, memoryview)):
                raise ValueError(f"binary draft field is forbidden: {name!r}")
        if len(self.to_json().encode()) > MAX_ENTRY_BYTES:
            raise ValueError("draft transfer exceeds entry ceiling")

    def to_json(self) -> str:
        return json.dumps(
            {
                "version": 1,
                "app": self.app,
                "routeFamily": self.route_family,
                "elementContract": self.element_contract,
                "schemaVersion": self.schema_version,
                "subject": self.subject,
                "fields": self.fields,
                "createdAt": self.created_at,
                "expiresAt": self.expires_at,
                "operationId": self.operation_id,
            },
            separators=(",", ":"),
            sort_keys=True,
        )


__all__ = [
    "DraftTransferEnvelope",
    "MAX_ENTRY_BYTES",
    "MAX_TTL_MS",
    "MAX_TTL_SECONDS",
    "draft_storage_key",
    "subject_fingerprint",
]

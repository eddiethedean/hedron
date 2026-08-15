"""Bounded browser-local draft transfer envelope (STATE-041)."""

from __future__ import annotations

import json
import time
from collections.abc import Mapping
from dataclasses import dataclass
from hashlib import sha256
from typing import Any

FORBIDDEN_FIELD_TOKENS = frozenset(
    {"auth", "authorization", "cookie", "csrf", "file", "html", "password", "secret", "token"}
)
MAX_ENTRY_BYTES = 32_768
MAX_TTL_SECONDS = 1800


def subject_fingerprint(subject: str, authority_revision: str) -> str:
    if not subject or not authority_revision:
        raise ValueError("subject and authority revision are required")
    return sha256(f"{subject}\0{authority_revision}".encode()).hexdigest()[:24]


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
        if not 1 <= ttl_seconds <= MAX_TTL_SECONDS:
            raise ValueError("draft TTL is outside the allowed range")
        timestamp = int(time.time()) if now is None else now
        envelope = cls(
            app=app,
            route_family=route_family,
            element_contract=element_contract,
            schema_version=schema_version,
            subject=subject,
            fields=dict(fields),
            created_at=timestamp,
            expires_at=timestamp + ttl_seconds,
            operation_id=operation_id,
        )
        envelope.validate(now=timestamp)
        return envelope

    @property
    def storage_key(self) -> str:
        parts = (
            self.app,
            self.route_family,
            self.element_contract,
            self.schema_version,
            self.subject,
        )
        digest = sha256("\0".join(parts).encode()).hexdigest()
        return f"hedron:draft:v1:{digest}"

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
        timestamp = int(time.time()) if now is None else now
        if self.expires_at <= timestamp or self.expires_at - self.created_at > MAX_TTL_SECONDS:
            raise ValueError("draft transfer is expired or exceeds maximum TTL")
        for name, value in self.fields.items():
            lowered = str(name).lower()
            if any(token in lowered for token in FORBIDDEN_FIELD_TOKENS):
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
                "route_family": self.route_family,
                "element_contract": self.element_contract,
                "schema_version": self.schema_version,
                "subject": self.subject,
                "fields": self.fields,
                "created_at": self.created_at,
                "expires_at": self.expires_at,
                "operation_id": self.operation_id,
            },
            separators=(",", ":"),
            sort_keys=True,
        )


__all__ = ["DraftTransferEnvelope", "MAX_ENTRY_BYTES", "MAX_TTL_SECONDS", "subject_fingerprint"]

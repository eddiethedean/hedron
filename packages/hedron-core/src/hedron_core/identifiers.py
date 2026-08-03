"""Deterministic identifier helpers for components and DOM instances."""

from __future__ import annotations

import base64
import hashlib
import json
from collections.abc import Mapping
from typing import Any

IDENTITY_FORMAT_VERSION = 1


def component_type_id(distribution: str, module: str, qualified_name: str) -> str:
    """Return ``<distribution>:<module>.<qualified-name>``."""
    return f"{distribution}:{module}.{qualified_name}"


def registry_resource_id(kind: str, logical_id: str) -> str:
    """Return ``<kind>:<logical-id>``."""
    return f"{kind}:{logical_id}"


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)


def _base32_lower(digest: bytes, length: int = 20) -> str:
    encoded = base64.b32encode(digest).decode("ascii").lower().rstrip("=")
    return encoded[:length]


def instance_id(identity_record: Mapping[str, Any]) -> str:
    """Return ``h-`` plus first 20 lowercase base32 chars of SHA-256."""
    payload = {"v": IDENTITY_FORMAT_VERSION, **dict(identity_record)}
    digest = hashlib.sha256(_canonical_json(payload).encode("utf-8")).digest()
    return f"h-{_base32_lower(digest)}"


def content_digest(data: bytes | str) -> str:
    if isinstance(data, str):
        data = data.encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def asset_filename_stem(digest_hex: str) -> str:
    return digest_hex[:20]

"""Stable cache-key materialization."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from typing import Any

from hedron_core.cache.types import CacheScope
from hedron_core.security import Secret


def _fingerprint(material: str) -> str:
    return hashlib.sha256(material.encode("utf-8")).hexdigest()[:24]


def _normalize_arg(value: Any) -> Any:
    if isinstance(value, Secret):
        # Non-reversible keyed transform — never store plaintext secret in key material.
        return {"__secret__": _fingerprint(repr(value.reveal()))}
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    # Request/dependency objects must never be serialized. Starlette Request is a
    # Mapping, so reject by type name before the Mapping branch.
    type_name = type(value).__name__
    if type_name in {"Request", "HTTPConnection"} or "Dependency" in type_name:
        raise ValueError(f"Cannot use {type_name} as a cache key argument")
    if isinstance(value, Mapping):
        return {
            str(k): _normalize_arg(v)
            for k, v in sorted(value.items(), key=lambda kv: str(kv[0]))  # type: ignore[misc]
        }
    if isinstance(value, (list, tuple)):
        return [_normalize_arg(v) for v in value]
    if hasattr(value, "model_dump"):
        return _normalize_arg(value.model_dump())
    return repr(value)


def build_cache_key(
    *,
    identity: str,
    args: tuple[object, ...] = (),
    kwargs: Mapping[str, object] | None = None,
    version: str = "1",
    scope: str = CacheScope.PRIVATE.value,
    vary: Mapping[str, object] | None = None,
) -> str:
    payload = {
        "identity": identity,
        "version": version,
        "scope": scope,
        "args": [_normalize_arg(a) for a in args],
        "kwargs": {k: _normalize_arg(v) for k, v in sorted((kwargs or {}).items())},
        "vary": {k: _normalize_arg(v) for k, v in sorted((vary or {}).items())},
    }
    material = json.dumps(payload, sort_keys=True, default=str, separators=(",", ":"))
    return _fingerprint(material)

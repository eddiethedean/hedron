"""Measured cached TypeAdapter / validate_json helpers. Not the FormBody path."""

from __future__ import annotations

import json
from collections.abc import Mapping
from functools import lru_cache
from typing import Any, TypeVar, cast

from pydantic import TypeAdapter, ValidationError

from hedron_core.codes import HED_FP_0007
from hedron_core.diagnostics import error
from hedron_core.type_schema import MAX_VALIDATION_ERRORS
from hedron_core.typing_aliases import JsonObject, JsonValue

__all__ = [
    "ADAPTER_CANDIDATES",
    "cached_type_adapter",
    "clear_type_adapter_cache",
    "validate_json_document",
]

ADAPTER_CANDIDATES = (
    "websocket-message",
    "mcp-envelope",
    "job-cache-record",
    "build-manifest",
    "remote-adapter-metadata",
    "bounded-data-batch",
)

T = TypeVar("T")


@lru_cache(maxsize=256)
def cached_type_adapter(type_: type[T] | str) -> TypeAdapter[Any]:
    """Reuse one TypeAdapter per type/version boundary."""
    if isinstance(type_, str):
        raise error(
            HED_FP_0007,
            title="TypeAdapter cache requires a concrete type",
            explanation="String type names are not a cache key for validate_json.",
            remediation="Pass the live Python type, not a delayed annotation string.",
        )
    return TypeAdapter(type_)


def clear_type_adapter_cache() -> None:
    """Rollback: restore current parsers by dropping the measured cache."""
    cached_type_adapter.cache_clear()


def _reject_duplicate_keys(pairs: list[tuple[str, JsonValue]]) -> dict[str, JsonValue]:
    out: dict[str, JsonValue] = {}
    for key, value in pairs:
        if key in out:
            raise error(
                HED_FP_0007,
                title="Duplicate JSON keys refused",
                explanation=f"Key {key!r} appeared more than once.",
                remediation="Emit canonical JSON without duplicate keys.",
            )
        out[key] = value
    return out


def validate_json_document(
    type_: type[T],
    document: str | bytes | Mapping[str, object],
    *,
    candidate: str = "bounded-data-batch",
    max_bytes: int = 65_536,
) -> T:
    """Direct JSON path with duplicate-key, size, and error bounds."""
    if candidate not in ADAPTER_CANDIDATES:
        raise error(
            HED_FP_0007,
            title="TypeAdapter candidate is not admitted",
            explanation=f"{candidate!r} is outside the measured adapter inventory.",
            remediation="Use a lock-file candidate or keep the existing parser.",
        )
    if isinstance(document, (str, bytes)):
        raw = document if isinstance(document, str) else document.decode("utf-8")
        if len(raw.encode("utf-8")) > max_bytes:
            raise error(
                HED_FP_0007,
                title="JSON document exceeds size bound",
                explanation=f"Document is larger than {max_bytes} bytes.",
                remediation="Split the batch or raise the measured bound with evidence.",
            )
        try:
            parsed = json.loads(raw, object_pairs_hook=_reject_duplicate_keys)
        except json.JSONDecodeError as exc:
            raise error(
                HED_FP_0007,
                title="Invalid JSON document",
                explanation=str(exc),
                remediation="Emit canonical UTF-8 JSON.",
            ) from exc
    else:
        parsed = dict(document)
    adapter = cached_type_adapter(type_)
    try:
        return adapter.validate_python(parsed)
    except ValidationError as exc:
        errors = exc.errors()[:MAX_VALIDATION_ERRORS]
        paths = [".".join(str(part) for part in item.get("loc", ())) for item in errors]
        raise error(
            HED_FP_0007,
            title="JSON document failed validation",
            explanation=f"invalid_paths={paths}",
            remediation="Fix the payload or restore the previous parser.",
        ) from exc


def validate_json_document_rollback(type_: type[T], document: str) -> JsonObject:
    """Restore current parser behavior: json.loads without TypeAdapter cache."""
    parsed: object = json.loads(document, object_pairs_hook=_reject_duplicate_keys)
    if not isinstance(parsed, dict):
        raise error(
            HED_FP_0007,
            title="JSON document is not an object",
            explanation="Rollback parsers still require an object.",
            remediation="Emit a JSON object.",
        )
    return cast(JsonObject, parsed)

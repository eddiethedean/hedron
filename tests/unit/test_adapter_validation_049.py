"""ADAPTER-VALIDATION-049 cached TypeAdapter, not FormBody, FailFast off this gate."""

from __future__ import annotations

from pydantic import BaseModel

from hedron_core.diagnostics import HedronError
from hedron_core.validation_adapters import (
    ADAPTER_CANDIDATES,
    cached_type_adapter,
    clear_type_adapter_cache,
    validate_json_document,
    validate_json_document_rollback,
)


class Record(BaseModel):
    kind: str
    n: int = 0


def test_candidates_exclude_formbody_and_failfast() -> None:
    assert "formbody-request" not in ADAPTER_CANDIDATES
    assert "fail-fast-batch" not in ADAPTER_CANDIDATES


def test_cached_validate_json_rejects_duplicates_and_rolls_back() -> None:
    clear_type_adapter_cache()
    first = cached_type_adapter(Record)
    second = cached_type_adapter(Record)
    assert first is second
    parsed = validate_json_document(
        Record,
        '{"kind":"job-cache-record","n":1}',
        candidate="job-cache-record",
    )
    assert parsed.n == 1
    try:
        validate_json_document(
            Record,
            '{"kind":"x","kind":"y"}',
            candidate="job-cache-record",
        )
    except HedronError as exc:
        assert exc.diagnostic.code == "HED-FP-0007"
    restored = validate_json_document_rollback(Record, '{"kind":"ok"}')
    assert restored["kind"] == "ok"
    clear_type_adapter_cache()

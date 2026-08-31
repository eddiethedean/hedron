"""Local backend capacity contracts."""

from __future__ import annotations

import pytest

from hedron_core.cache import InMemoryCacheBackend
from hedron_core.jobs import InMemoryJobBackend
from hedron_data.memory import InMemoryDataSource


def test_memory_cache_evicts_oldest_entry_when_capacity_is_reached() -> None:
    cache = InMemoryCacheBackend(max_entries=1, max_bytes=1000)
    cache.set("first", {"value": 1})
    cache.set("second", {"value": 2})
    assert cache.get("first") is None
    assert cache.get("second") == {"value": 2}


def test_memory_cache_rejects_oversized_entry() -> None:
    cache = InMemoryCacheBackend(max_entries=2, max_bytes=4)
    with pytest.raises(ValueError, match="max_bytes"):
        cache.set("large", "too-large")


def test_memory_cache_failed_copy_leaves_existing_value() -> None:
    class BadCopy:
        def __deepcopy__(self, memo: dict[int, object]) -> object:
            del memo
            raise RuntimeError("copy failed")

    cache = InMemoryCacheBackend(max_entries=2, max_bytes=1000)
    cache.set("stable", {"value": 1})
    with pytest.raises(RuntimeError, match="copy failed"):
        cache.set("stable", BadCopy())
    assert cache.lookup("stable") == (True, {"value": 1})


def test_memory_job_backend_rejects_oversized_payload() -> None:
    backend = InMemoryJobBackend(max_jobs=2, max_payload_bytes=4)
    with pytest.raises(ValueError, match="max_payload_bytes"):
        backend.submit("demo", {"value": "too-large"})


def test_memory_data_source_has_a_row_capacity() -> None:
    with pytest.raises(ValueError, match="max_rows"):
        InMemoryDataSource([{"id": "1"}, {"id": "2"}], max_rows=1)

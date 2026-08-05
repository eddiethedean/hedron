"""Production / strict durable-backend gates."""

from __future__ import annotations

import warnings

import pytest

from hedron_core.cache import InMemoryCacheBackend, set_cache_backend
from hedron_core.jobs import InMemoryJobBackend, set_job_backend
from hedron_core.production_gate import assert_durable_backends, refuse_in_memory_backends


def test_refuse_in_memory_backends_raises() -> None:
    set_job_backend(InMemoryJobBackend())
    set_cache_backend(InMemoryCacheBackend())
    with pytest.raises(RuntimeError, match="InMemoryJobBackend"):
        refuse_in_memory_backends()


def test_assert_durable_backends_warns_under_strict_only(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("HEDRON_ENV", raising=False)
    set_job_backend(InMemoryJobBackend())
    set_cache_backend(InMemoryCacheBackend())
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        assert_durable_backends(production=False, strict_profile=True)
    assert any("strict" in str(w.message).lower() for w in caught)


def test_assert_durable_backends_raises_in_production(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("HEDRON_ENV", "production")
    set_job_backend(InMemoryJobBackend())
    set_cache_backend(InMemoryCacheBackend())
    with pytest.raises(RuntimeError, match="InMemory"):
        assert_durable_backends(production=True, strict_profile=False)

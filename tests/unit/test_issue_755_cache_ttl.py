"""Regression coverage for #755 cache TTL validation."""

from __future__ import annotations

import math

import pytest

import edron as ed
from hedron import cache_component, cache_data
from hedron_core.cache import InMemoryCacheBackend


@pytest.mark.parametrize("ttl", [math.nan, math.inf, -math.inf, True])
def test_native_cache_decorators_reject_invalid_ttl_at_definition(ttl: object) -> None:
    with pytest.raises(ValueError, match="finite number"):

        @cache_data(ttl=ttl)  # type: ignore[arg-type]
        def cached_data() -> int:
            return 1

    with pytest.raises(ValueError, match="finite number"):

        @cache_component(ttl=ttl)  # type: ignore[arg-type]
        def cached_component() -> str:
            return "ok"


@pytest.mark.parametrize("ttl", [math.nan, math.inf, -math.inf, True])
def test_in_memory_cache_rejects_invalid_ttl_without_writing(ttl: object) -> None:
    backend = InMemoryCacheBackend()
    with pytest.raises(ValueError, match="finite number"):
        backend.set("x", {"value": 1}, ttl=ttl)  # type: ignore[arg-type]
    assert backend.lookup("x") == (False, None)


@pytest.mark.parametrize("ttl", [math.nan, math.inf, -math.inf, True])
def test_edron_cache_rejects_invalid_ttl_at_definition(ttl: object) -> None:
    with pytest.raises(ValueError, match="finite number"):

        @ed.cache_data(ttl=ttl)  # type: ignore[arg-type]
        def cached() -> int:
            return 1

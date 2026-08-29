"""Cache protocols, keying, single-flight, and in-memory backend."""

from __future__ import annotations

from hedron_core.cache.backend import CacheBackend
from hedron_core.cache.gate import (
    get_cache_backend,
    invalidate_tags,
    reset_cache_for_tests,
    set_cache_backend,
    use_cache_backend,
)
from hedron_core.cache.keying import build_cache_key
from hedron_core.cache.memory import InMemoryCacheBackend
from hedron_core.cache.tracing import CacheTrace, get_cache_traces, record_cache_trace
from hedron_core.cache.types import CacheEvent, CacheScope

__all__ = [
    "CacheBackend",
    "CacheEvent",
    "CacheScope",
    "CacheTrace",
    "InMemoryCacheBackend",
    "build_cache_key",
    "get_cache_backend",
    "get_cache_traces",
    "invalidate_tags",
    "record_cache_trace",
    "reset_cache_for_tests",
    "set_cache_backend",
    "use_cache_backend",
]

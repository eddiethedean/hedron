"""Production / strict profile backend gates."""

from __future__ import annotations

import warnings

from hedron_core.cache import InMemoryCacheBackend, get_cache_backend
from hedron_core.compile_gate import is_production_env
from hedron_core.jobs import InMemoryJobBackend, get_job_backend

__all__ = ["assert_durable_backends", "refuse_in_memory_backends"]


def refuse_in_memory_backends(*, jobs: bool = True, cache: bool = True) -> None:
    """Raise when process-local job/cache backends are active under production."""
    if jobs and isinstance(get_job_backend(), InMemoryJobBackend):
        raise RuntimeError(
            "InMemoryJobBackend is not allowed under HEDRON_ENV=production. "
            "Call set_job_backend(...) with Redis/Celery/RQ, or unset production "
            "for local demos."
        )
    if cache and isinstance(get_cache_backend(), InMemoryCacheBackend):
        raise RuntimeError(
            "InMemoryCacheBackend is not allowed under HEDRON_ENV=production. "
            "Call set_cache_backend(...) with an external store, or unset production "
            "for local demos."
        )


def assert_durable_backends(
    *,
    production: bool | None = None,
    strict_profile: bool = False,
) -> None:
    """Enforce durable backends in production; warn under strict-only profiles."""
    if is_production_env(production=production):
        refuse_in_memory_backends()
        return
    if strict_profile and (
        isinstance(get_job_backend(), InMemoryJobBackend)
        or isinstance(get_cache_backend(), InMemoryCacheBackend)
    ):
        warnings.warn(
            "security='strict' with in-memory job/cache backends is not multi-worker safe; "
            "configure set_job_backend / set_cache_backend before production.",
            UserWarning,
            stacklevel=3,
        )

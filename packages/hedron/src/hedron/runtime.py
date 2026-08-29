"""Application-owned runtime state.

The original 1.0 APIs use module-level helpers for registration and service
lookups.  This module gives those helpers an application scope without making
existing callers rewrite all imports at once.  The process-level helpers remain
as a compatibility fallback for core-only and test usage.
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable, Mapping
from contextlib import ExitStack
from typing import Any

from hedron.concurrency import ConcurrencyConfig, ConcurrencyLimiter, use_limiter
from hedron.tracing import TraceConfig, use_trace_config
from hedron_core.cache import (
    CacheTraceState,
    get_cache_backend,
    new_cache_trace_state,
    use_cache_backend,
    use_cache_trace_state,
)
from hedron_core.cache.backend import CacheBackend
from hedron_core.catalog import (
    InteractionCatalog,
    ProjectionProvider,
    new_projection_registry,
    use_catalog_context,
    use_projection_registry,
)
from hedron_core.durability import is_process_local
from hedron_core.jobs import get_job_backend, use_job_backend
from hedron_core.jobs.backend import JobBackend
from hedron_core.plugins.explorer import (
    PluginRegistryState,
    new_plugin_registry,
    use_plugin_registry,
)
from hedron_core.registry import RegistryBuilder, fork_registry_builder, use_registry_builder

__all__ = ["HedronRuntimeContext", "RuntimeContextMiddleware"]


class HedronRuntimeContext:
    """Mutable application-owned services with immutable lifecycle boundaries."""

    def __init__(
        self,
        *,
        registry: RegistryBuilder,
        cache: CacheBackend,
        jobs: JobBackend,
        concurrency: ConcurrencyConfig,
        tracing: TraceConfig,
        plugins: PluginRegistryState,
        projections: dict[str, ProjectionProvider],
        cache_traces: CacheTraceState,
    ) -> None:
        self.registry = registry
        self.cache = cache
        self.jobs = jobs
        self.concurrency = concurrency
        self.tracing = tracing
        self.plugins = plugins
        self.projections = projections
        self.cache_traces = cache_traces
        self.limiter = ConcurrencyLimiter(concurrency)
        self.catalog: InteractionCatalog | None = None

    @classmethod
    def from_defaults(cls) -> HedronRuntimeContext:
        """Create an isolated context seeded from installed package defaults."""
        cache = get_cache_backend()
        jobs = get_job_backend()
        # Process-local defaults must not be shared by two applications.
        if is_process_local(cache):
            from hedron_core.cache import InMemoryCacheBackend

            cache = InMemoryCacheBackend()
        if is_process_local(jobs):
            from hedron_core.jobs import InMemoryJobBackend

            jobs = InMemoryJobBackend()

        from hedron.concurrency import get_concurrency_config
        from hedron.tracing import get_trace_config

        current_concurrency = get_concurrency_config()
        concurrency = ConcurrencyConfig(
            enabled=current_concurrency.enabled,
            max_in_flight=current_concurrency.max_in_flight,
            degrade_at=current_concurrency.degrade_at,
            prepare_deadline_seconds=current_concurrency.prepare_deadline_seconds,
        )
        current_trace = get_trace_config()
        tracing = TraceConfig(
            enabled=current_trace.enabled,
            sample_rate=current_trace.sample_rate,
            service_name=current_trace.service_name,
        )
        return cls(
            registry=fork_registry_builder(),
            cache=cache,
            jobs=jobs,
            concurrency=concurrency,
            tracing=tracing,
            plugins=new_plugin_registry(),
            projections=new_projection_registry(),
            cache_traces=new_cache_trace_state(),
        )

    def activate(self) -> ExitStack:
        """Return a context manager binding all application-owned services."""
        stack = ExitStack()
        stack.enter_context(use_registry_builder(self.registry))
        stack.enter_context(use_plugin_registry(self.plugins))
        stack.enter_context(use_projection_registry(self.projections))
        stack.enter_context(use_catalog_context(self.catalog))
        stack.enter_context(use_cache_backend(self.cache))
        stack.enter_context(use_cache_trace_state(self.cache_traces))
        stack.enter_context(use_job_backend(self.jobs))
        stack.enter_context(use_limiter(self.limiter))
        stack.enter_context(use_trace_config(self.tracing))
        return stack


class RuntimeContextMiddleware:
    """Pure ASGI middleware that binds the owning app context per request."""

    def __init__(self, app: Callable[..., Awaitable[Any]], runtime: HedronRuntimeContext) -> None:
        self.app = app
        self.runtime = runtime

    async def __call__(
        self,
        scope: Mapping[str, Any],
        receive: Callable[..., Awaitable[Any]],
        send: Callable[..., Awaitable[Any]],
    ) -> None:
        if scope.get("type") not in {"http", "websocket"}:
            await self.app(scope, receive, send)
            return
        with self.runtime.activate():
            await self.app(scope, receive, send)

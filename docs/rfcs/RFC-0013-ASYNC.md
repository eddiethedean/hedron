# RFC-0013: Async architecture

**Status:** Proposed

## Model

Endpoints, addressable factories, actions, dependencies, data sources, cache loaders, and plugin lifecycles may be synchronous or asynchronous. There is no separate async component type. Hedron awaits declared work while leaving concurrency explicit where it affects correctness.

Tree rendering and serialization remain synchronous and deterministic. A future advanced `prepare()` lifecycle may perform asynchronous I/O before `render()`, but endpoint factories and sources are the MVP path.

## Concurrency and cancellation

Structured concurrency uses `TaskGroup` or AnyIO equivalents. Request cancellation propagates to request-owned work; `CancelledError` is not swallowed. Timeouts are explicit and may produce error, fallback, stale-cache, or partial-region policies. Detached request tasks are diagnosed.

Lazy addressable components are the default deferred UI. Small post-response work uses FastAPI `BackgroundTasks`; durable or CPU-heavy work uses an external job backend. General streamed documents, SSE, and WebSockets are deferred.

## Acceptance criteria

- One application safely mixes `def` and `async def` routes and dependencies.
- Yield dependencies remain alive through rendering and streaming iteration.
- Blocking I/O is never silently executed on the event loop.
- Cancellation, timeout, cleanup, and lifespan ordering have tests and Explorer traces.


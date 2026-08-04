# RFC-0013: Async architecture

**Status:** Accepted

**Revision:** 2026-08-03 — D-035 made cancellation and lifecycle guarantees capability-aware across
ASGI and WSGI adapters and made the durable job baseline explicit.

## Model

Endpoints, addressable factories, actions, dependencies, data sources, cache loaders, and plugin lifecycles may be synchronous or asynchronous. There is no separate async component type. Hedron awaits declared work while leaving concurrency explicit where it affects correctness.

Tree rendering and serialization remain synchronous and deterministic. A future advanced `prepare()` lifecycle may perform asynchronous I/O before `render()`, but endpoint factories and sources are the MVP path.

## Concurrency and cancellation

Structured concurrency uses `TaskGroup` or AnyIO equivalents. Under an adapter/server combination
that exposes disconnect cancellation, request cancellation propagates to request-owned work and
`CancelledError` is not swallowed. Other combinations expose cooperative checkpoints and deadlines
without claiming end-to-end disconnect propagation. Timeouts are explicit and may produce error,
fallback, stale-cache, or partial-region policies. Detached request tasks are diagnosed.

Lazy addressable components are the default deferred UI. Small post-response work uses the host
framework's bounded background mechanism where one exists; durable or CPU-heavy work uses an
external job backend. The required 202 job interaction uses accessible bounded polling.
Phase 0.10 adds official SSE observation, focused streaming primitives, and accepted page/session
WebSocket channels per [RFC-0032](RFC-0032-LIVE-TRANSPORT.md). General streamed HTML for every
component remains forbidden (D-019); polling remains the Supported job-status fallback.

`hedron.gather()` defines named results, sibling-failure and explicit partial-failure behavior, and
request-scope ownership. `hedron.run_sync()` defines `ContextVar` propagation, a capacity limiter,
cancellation behavior, and rejects CPU-heavy work. These helpers do not create a second scheduler.

## Acceptance criteria

- One application safely mixes `def` and `async def` routes and dependencies.
- Yield dependencies remain alive through rendering and streaming iteration.
- Blocking I/O is never silently executed on the event loop.
- Cancellation, timeout, cleanup, and lifespan ordering have tests and Explorer traces.
- The capability matrix distinguishes disconnect cancellation, cooperative deadlines, background
  work, and lifecycle guarantees for each supported framework/server combination.
- Job tests cover idempotency, authorization/tenant scope, state transitions, retry/failure,
  retention, cancellation requests, and backend degradation.

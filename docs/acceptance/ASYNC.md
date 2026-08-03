# Async acceptance

Phase 0.7 async claims are capability-aware: ASGI disconnect propagation, WSGI cooperative
deadlines, framework background mechanisms, and portable structured-concurrency behavior are
reported separately. Durable work is additionally owned by [JOBS.md](JOBS.md), and evidence follows
[EVIDENCE.md](EVIDENCE.md).

## Behavior

- [x] One application safely mixes sync and async pages and dependencies on the FastAPI MVP surface.
- [x] Yield dependencies clean up after ordinary rendering and response iteration.
- [ ] Supported ASGI adapter/server combinations propagate request disconnects to request-owned work
  without leaking tasks or resources; other combinations document cooperative behavior.
- [ ] Structured child failure cancels siblings unless partial failure is explicit.
- [ ] Timeout policies produce documented error, fallback, retry, stale-cache, or partial results.
- [x] Lazy components expose usable busy and retry states (markup + HTMX load trigger).
- [ ] Blocking I/O is diagnosed or intentionally run through the supported thread bridge.
- [ ] CPU-heavy and durable work is represented through the `JobBackend` interaction contract.

## Testing and observability

- [ ] pytest-anyio fixtures cover all async public protocols.
- [ ] Explorer separates dependency, I/O, render, serialize, cache, cancellation, and timeout timing.
- [ ] Lifespan starts in dependency order and shuts down in reverse order.
- [ ] Cancellation and timeout traces redact sensitive values.

## Exit

Stress tests show no task growth, session leak, or event-loop blocking under repeated aborted HTMX requests.

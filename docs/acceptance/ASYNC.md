# Async acceptance

## Behavior

- [ ] One application safely mixes sync and async pages, components, actions, dependencies, sources, and plugin hooks.
- [ ] Yield dependencies clean up after ordinary rendering and response iteration.
- [ ] Request disconnect cancels all request-owned work without leaking tasks or resources.
- [ ] Structured child failure cancels siblings unless partial failure is explicit.
- [ ] Timeout policies produce documented error, fallback, retry, stale-cache, or partial results.
- [ ] Lazy components expose usable busy, timeout, error, and retry states.
- [ ] Blocking I/O is diagnosed or intentionally run through the supported thread bridge.
- [ ] CPU-heavy and durable work is represented through external jobs.

## Testing and observability

- [ ] pytest-anyio fixtures cover all async public protocols.
- [ ] Explorer separates dependency, I/O, render, serialize, cache, cancellation, and timeout timing.
- [ ] Lifespan starts in dependency order and shuts down in reverse order.
- [ ] Cancellation and timeout traces redact sensitive values.

## Exit

Stress tests show no task growth, session leak, or event-loop blocking under repeated aborted HTMX requests.


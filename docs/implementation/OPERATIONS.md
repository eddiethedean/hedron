# Production operations implementation

## Deployment topology

The FastAPI reference topology uses a reviewed ASGI server, multiple workers, a path-prefixed
reverse proxy, external static assets, and executable external cache/job conformance
implementations. Flask and Django slices exercise their declared WSGI/ASGI capability sets.

## Configuration and health

Configuration records proxy trust, public origin, root path/script name, asset origin, manifest,
cache/job backend, deadlines, and shutdown policy. Unsafe ambiguity fails closed. Liveness reports
process health; readiness reports whether required integrations can serve accepted work.

## Lifecycle

Startup validates manifests and starts resources in dependency order. Shutdown stops acceptance of
new durable work, drains bounded request/background work according to policy, closes resources in
reverse order, and emits a redacted result. Correctness-critical state is never process-local in a
multi-worker claim.

## Verification

Container/proxy tests cover URLs, forwarded headers, HTTPS, CSRF, cache variation, assets, worker
replacement, dependency degradation, graceful termination, offline startup, and rollback from
published artifacts.

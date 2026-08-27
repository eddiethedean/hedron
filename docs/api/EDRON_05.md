---
status: implemented
---

# Edron 0.5 resource and operational API

Edron 0.5 lowers resource, cache, job, and deployment ergonomics to native Hedron authorities.
It does not provide a worker, scheduler, queue, database, object store, or distributed cache.

## Resources

Register a lazy, app-owned resource through `App.resource(...)`:

```python
database = app.resource(
    "database",
    create_database,
    kind="custom",
    secret_refs={"dsn": "DATABASE_URL"},
)
```

The returned `Dependency` can be assigned to a `Page` field. The native
`hedron.connections.ConnectionRegistry` creates one application-scoped instance, and the native
lifespan closes it through `close`, `dispose`, `shutdown`, or `aclose` as appropriate. Factories
are never resolved by registration, explanation, or operations diagnostics.

`Resource`, `ConnectionRegistry`, and `ConnectionSpec` retain native ownership of resource
metadata. Secret values must be opaque references; diagnostics include names, kinds, and health
check labels only.

## Cache

`edron.cache_data(...)` is a thin wrapper over Hedron's native cache backend:

```python
@ed.cache_data(
    ttl=60,
    scope="tenant",
    vary_on=("tenant_id",),
    max_entries=128,
    tags=("summary",),
)
def load_summary(tenant_id: str) -> dict[str, int]:
    ...
```

TTL, scope validation, tag invalidation, single-flight computation, deep-copy isolation, and
process-local/durable backend policy come from native Hedron. `invalidate(...)` and
`invalidate_all()` route through that same backend; cached values never become durable truth.

## Jobs and live observation

`JobFlow` projects native `TaskFlow` and accepts an explicit `JobBackend`, bounded native polling
interval, retry-attempt metadata, and result-retention policy:

```python
flow = ed.JobFlow(
    name="report",
    input_model=ReportInput,
    job_type="report",
    payload=to_payload,
    backend=backend,
    scope=scope,
    result=render_result,
    poll_interval_ms=2000,
    retry_attempts=2,
)
app.include(flow)
```

Submit, status, cancel, and result routes use one `JobScope`; unknown or mismatched scope is a
404. Polling and ordinary HTTP/no-JavaScript behavior remain canonical. `job_status_events(...)`
only formats an already-authorized native `JobStatus` as bounded SSE events; it never performs a
lookup or authorization decision.

## Operations diagnostics

`app.operations()` (also available as `app.diagnostics()`) returns schema `edron.operations/1` with
production mode, job/cache backend type and durability, unresolved resource metadata, and explicit
limitations. `edron doctor` includes these facts when given an application. It never resolves a
resource, imports application callbacks, or emits secrets, payloads, session values, or filesystem
paths.

## Stability and ownership

These Edron names are Beta facades. Native Hedron owns dependency injection, lifespan, cache and
job backends, session storage, live transports, authorization, production gates, and adapter
behavior. Optional adapters remain lazy and must be directly installed and version-compatible.

See the [Phase 0.5 acceptance packet](https://github.com/eddiethedean/hedron/blob/main/docs/acceptance/EDRON_005.md)
and the [Edron roadmap](../EDRON_ROADMAP.md).

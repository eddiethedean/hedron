# What's new in 0.13

!!! note "Historical release note"

    This page records the 0.x release named in its title. For current installation,
    support, and published 1.0 status, use [Current release and support](current-release.md).
    Keep the historical pins below only when maintaining that release line.

Phase **0.13** — advanced async and observability (`v0.13.0`, published).

## Highlights

- Optional component `prepare()` before sync `render()` (ownership, deadlines, cancel, cache)
- Adaptive concurrency with semantic-preserving opt-out
- Optional distributed tracing via `hedron[otel]` / `configure_tracing`
- HDJ async filter/global I/O budgets, deadlines, and cancellation (`HDJ-DEF-013`)
- `SecurityAuditSink` for CSRF / HTMX target / Explorer / production-gate events
- Celery/RQ `JobBackend` status + idempotency require shared Redis (multi-worker durable)
- Live transports remain **experimental**; polling is the Supported production fallback
- Complete `HED-*` catalog with `scripts/check_hed_codes.py` CI gate

## Upgrade

See [Upgrade](upgrade.md) §0.13 and [What's ready](whats-ready.md).

## Install

```bash
pip install "hedron>=0.13.0" "uvicorn[standard]"
```

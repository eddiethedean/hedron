# Release notes

Train-level summary for the published **0.13.x** line. Package changelogs remain the
detailed record; this page is the adopter-facing index.

## Current train — 0.13.0 (2026-08-05)

**Published** coordinated train (`v0.13.0`). Advanced async and observability: optional
component `prepare()`, adaptive concurrency, optional OpenTelemetry, HDJ async I/O budgets,
`SecurityAuditSink`, Redis-durable Celery/RQ status, live-transport claim honesty, and a
complete `HED-*` catalog.

Narrative: [What's new in 0.13](whats-new-0.13.md) · maturity:
[What's ready today](whats-ready.md).

Install: `pip install -U "hedron>=0.13.0"` (or `uv add "hedron>=0.13.0"`).

## 0.12.0 — data and visualization scale

**Published** (`v0.12.0`). DataEditor scale, TransformPlan, beginner charts, optional viz
adapters, and HDJ data/charts parity (D-047). Narrative:
[What's new in 0.12](whats-new-0.12.md).

## 0.11.0 — native Flask/Django depth

**Published** coordinated train (`v0.11.0`). Native Flask/Django depth, bounded QuerySet
DataSource, Django forms bridge, portable adapter harness, HDJ inventory/CSP, and Celery/RQ
job bridges (D-046).

Narrative: [What's new in 0.11](whats-new-0.11.md).

## 0.10.1 — security / correctness patch

Fail-closed caching, safer redirects, hardened live-transport headers, shared job
SSE/poll authz. Narrative: [What's new in 0.10.1](whats-new-0.10.1.md).

## 0.10.0 — live interaction phase

Official SSE helpers, focused streaming, WebSocket page/session channels, navigation
preload, Chat/Dialog surfaces, and bundled HTMX SSE/head-support extensions.

Narrative: [What's new in 0.10](whats-new-0.10.md) · [Upgrade (0.8 → 0.13)](upgrade.md).

## Package changelogs (GitHub)

- [hedron](https://github.com/eddiethedean/hedron/blob/main/packages/hedron/CHANGELOG.md)
- [hedron-core](https://github.com/eddiethedean/hedron/blob/main/packages/hedron-core/CHANGELOG.md)
- [hedron-data](https://github.com/eddiethedean/hedron/blob/main/packages/hedron-data/CHANGELOG.md)
- [hedron-charts](https://github.com/eddiethedean/hedron/blob/main/packages/hedron-charts/CHANGELOG.md)
- [hedron-flask](https://github.com/eddiethedean/hedron/blob/main/packages/hedron-flask/CHANGELOG.md)
- [hedron-django](https://github.com/eddiethedean/hedron/blob/main/packages/hedron-django/CHANGELOG.md)
- [hedron-jinja](https://github.com/eddiethedean/hedron/blob/main/packages/hedron-jinja/CHANGELOG.md)
- [hedron-explorer](https://github.com/eddiethedean/hedron/blob/main/packages/hedron-explorer/CHANGELOG.md)

GitHub Releases: [eddiethedean/hedron/releases](https://github.com/eddiethedean/hedron/releases).

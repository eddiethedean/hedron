# Release notes

Train-level summary for the **0.17.x** line (**Published**). Package changelogs remain the
detailed record; this page is the adopter-facing index.

## Current train — 0.17.0 (2026-08-06)

**Published** (`v0.17.0`). Reactive dashboards and agent interfaces: `DashboardBinding` /
`InteractionGraph` / `TriggerContext`, `PropertyPatch` / `CollectionPatch`, cross-filter and
recorder/replay, HTMX shell primitives (`NavLink`, `OobHost`, `AppShell`), public
`render_interaction`, Dialog/Tabs/Pagination/Lazy markup asserts, full `error-codes.md`
alignment, and optional Alpha `hedron-notebook` / `hedron-mcp` (Experimental).

Narrative: [What's new in 0.17](whats-new-0.17.md) · maturity:
[What's ready today](whats-ready.md) · upgrade: [Upgrade (→ 0.17)](upgrade.md).

Install: `pip install -U "hedron>=0.17.0"` (or `uv add "hedron>=0.17.0"`).
Optional: `pip install "hedron[extras]"` · `"hedron[notebook]"` · `"hedron[mcp]"`.

Package changelogs: [hedron](https://github.com/eddiethedean/hedron/blob/main/packages/hedron/CHANGELOG.md) ·
[hedron-core](https://github.com/eddiethedean/hedron/blob/main/packages/hedron-core/CHANGELOG.md) ·
[hedron-notebook](https://github.com/eddiethedean/hedron/blob/main/packages/hedron-notebook/CHANGELOG.md) ·
[hedron-mcp](https://github.com/eddiethedean/hedron/blob/main/packages/hedron-mcp/CHANGELOG.md).

## 0.16.0 (2026-08-06)

**Published** (`v0.16.0`). Curated extras and analysis workbenches: optional `hedron-extras`
with FeatureManifest discovery, composition UI, DataExplorer/JSONEditor/CodeEditor (CSP-safe
host stub), ChartWorkbench, image tools, calendar/signature/typeahead, display recipes,
browser-Python sandbox, and Experimental specialty extras (TerminalView / joystick / device).

## 0.15.0 (2026-08-05)

**Published** (`v0.15.0`). Data-app surface completeness: AppScenario / HTMX testing helpers
(#22–#26), `region`/`@fragment`/`swap`, typed controls and surface chrome, media
Range/downloads, Map/GeoJSON, BrowserContext/Storage, Math/IFrame, OIDC/session helpers, and
the connection registry.

## 0.14.0 (2026-08-05)

**Published** coordinated train (`v0.14.0`). Portable runtimes and acceleration (D-048):
language-neutral `hedron-conformance` kit, experimental Java/Node runtimes, optional
`hedron-native` HTML-escape acceleration with pure-Python fallback, and HDJ instrumentation
(`HDJ-DEF-014`).

Narrative: [What's new in 0.14](whats-new-0.14.md) · maturity:
[What's ready today](whats-ready.md).

Install: `pip install -U "hedron>=0.14.0"` (or `uv add "hedron>=0.14.0"`).
Optional: `pip install "hedron[conformance]" "hedron[native]"`.

## 0.13.0 — advanced async and observability

**Published** (`v0.13.0`). Optional component `prepare()`, adaptive concurrency, optional
OpenTelemetry, HDJ async I/O budgets, `SecurityAuditSink`, Redis-durable Celery/RQ status,
live-transport claim honesty, and a complete `HED-*` catalog.

Narrative: [What's new in 0.13](whats-new-0.13.md).

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

See package changelogs and the archive for earlier trains.

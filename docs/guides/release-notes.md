# Release notes

Train-level summary for the **0.18.x** line (**Published**). Package changelogs remain the
detailed record; this page is the adopter-facing index. Aggregated links:
[Changelog](changelog.md).

## Current train — 0.18.0 (2026-08-06)

**Published** (`v0.18.0`). Model demos and inference workflows: `InferenceInterface` /
`ModelDemo`, `ExampleSet` / presentation builtins / `PredictionFeedback`, `InferencePolicy`
over `JobBackend`, `InteractionRecorder`, `InferenceWorkflow` with structured editor, and
optional Alpha `hedron-gradio` (Experimental).

Narrative: [What's new in 0.18](whats-new-0.18.md) · maturity:
[What's ready today](whats-ready.md) · Gradio: [Gradio migration](gradio-migration.md).

Install: `pip install -U "hedron>=0.18.0"` (or `uv add "hedron>=0.18.0"`).
Optional: `pip install "hedron[gradio]"` · `"hedron[notebook]"` · `"hedron[mcp]"`.

Package changelogs: [hedron](https://github.com/eddiethedean/hedron/blob/main/packages/hedron/CHANGELOG.md) ·
[hedron-core](https://github.com/eddiethedean/hedron/blob/main/packages/hedron-core/CHANGELOG.md) ·
[hedron-gradio](https://github.com/eddiethedean/hedron/blob/main/packages/hedron-gradio/CHANGELOG.md).

## 0.17.0 (2026-08-06)

**Published** (`v0.17.0`). Reactive dashboards and agent interfaces: `DashboardBinding` /
`InteractionGraph` / `TriggerContext`, `PropertyPatch` / `CollectionPatch`, cross-filter and
recorder/replay, HTMX shell primitives (`NavLink`, `OobHost`, `AppShell`), public
`render_interaction`, Dialog/Tabs/Pagination/Lazy markup asserts, full `error-codes.md`
alignment, and optional Alpha `hedron-notebook` / `hedron-mcp` (Experimental).

Narrative: [What's new in 0.17](whats-new-0.17.md).

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

**Published** (`v0.14.0`). Portable runtimes and acceleration: conformance kit, experimental
Java/Node runtimes, optional Rust HTML-escape acceleration, HDJ instrumentation.

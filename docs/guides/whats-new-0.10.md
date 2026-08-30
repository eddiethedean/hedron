# What's new in 0.10

!!! note "Historical release note"

    This page records the 0.x release named in its title. For current installation,
    support, and published 1.0 status, use [Current release and support](current-release.md).
    Keep the historical pins below only when maintaining that release line.

The coordinated **`0.10.1`** train (initial cut `0.10.0`) adds live interaction on top of the 0.9 HDJ authoring
line. Full detail: [What's ready](whats-ready.md) · [Upgrade](upgrade.md) ·
[Live interaction](live-interaction.md).

## Highlights

- Official HTMX **SSE** observation (`SseResponse`, `job_status_sse_response`) on FastAPI
- **Focused streaming** (`StreamingComponentResponse`, token/list/document helpers)
- **Page/session WebSocket** channels with origin checks
- **Dialog** / **ChatMessage** / **ChatInput** components
- Opt-in **navigation preload** (`NavigationPreloadPolicy`)
- HDJ head / two-phase streaming helpers in `hedron-jinja`

## Still Deferred / honest gaps

- Full three-engine live browser matrix, load/proxy backpressure evidence, Explorer live
  traces → owned `0.10.x` Deferred rows in STATUS

Native Flask/Django depth, QuerySet DataSource, and Django forms shipped in **0.11** —
see [What's new in 0.11](whats-new-0.11.md).

## Upgrade path

1. If you still need HDN, stay on **0.8** until templates are rewritten.
2. Move to **0.9** for HDJ (`hedron[jinja]`), then to **0.10** for live helpers.
3. Keep polling as the Supported job-status fallback even when you add SSE.

# Architecture overview

Hedron is typed, server-rendered UI for Python web apps. The flagship `hedron` package
extends FastAPI; `hedron-core` renders portable components; Flask/Django adapters share
the same renderer without FastAPI.

## Request lifecycle (FastAPI)

```mermaid
sequenceDiagram
  participant Browser
  participant Middleware
  participant HedronRoute
  participant Handler
  participant Renderer
  Browser->>Middleware: HTTP request
  Middleware->>HedronRoute: CSRF session security as configured
  HedronRoute->>Handler: DI parsed props
  Handler-->>HedronRoute: Page InteractionResult or Response
  HedronRoute->>Renderer: PAGE or FRAGMENT mode
  Renderer-->>HedronRoute: safe HTML plus assets
  HedronRoute-->>Browser: HTML HTMX headers
```

1. The request enters ordinary FastAPI/Starlette middleware (sessions, CORS, your auth).
2. `HedronRoute` uses FastAPI for parsing, dependency injection, and exceptions.
3. Built-in security profiles validate CSRF on unsafe methods when enabled.
4. Your `@app.page` / `@app.component` / `@app.action` handler returns a `Page`,
   `InteractionResult`, model, or explicit response.
5. Hedron selects **PAGE** (full document) or **FRAGMENT** (region HTML) from HTMX
   headers and declared `FragmentRegion` policy — unauthorized targets fail closed.
6. `hedron-core` builds a node tree, collects assets, and serializes escaped HTML.
7. The response may include approved HTMX headers from `InteractionResult`.
8. The browser (HTMX) swaps markup; optional SSE/WebSocket helpers observe or push
   updates (FastAPI flagship; polling remains the Supported fallback).

### Flask / Django

Adapters (`hedron_route` / `hedron_view`, `respond`, `interaction_response`) authorize
fragment/OOB policy and merge validated HTMX headers, then call the same renderer. Host
middleware owns sessions/CSRF/auth. Official HTMX SSE helpers are FastAPI-only and
**experimental** (`hedron.experimental`); polling is the Supported fallback.

## PAGE vs FRAGMENT

| Mode | When | Typical return |
|---|---|---|
| PAGE | Navigation / full document | `Page(...)` |
| FRAGMENT | `HX-Request` targeting a declared region | `InteractionResult(content=..., region_id=...)` |

Rendering a component never implies a public route — only `@page` / `@component` /
`@action` (or adapter equivalents) expose HTTP endpoints.

## Multi-worker, jobs, and inference

### Sessions and jobs across workers

- In-memory session or job state does **not** span processes — use sticky sessions or an
  external store (`RedisJobBackend`, `CeleryJobBackend`, or `RQJobBackend`).
- Every web process must call `set_job_backend(...)` with the same Redis prefix/TTL.
- Scope durable jobs with `auth_subject` / `tenant_id`; HTTP status helpers fail closed for
  unscoped jobs. See [Jobs](api/JOBS.md) and [Celery / RQ + Redis](guides/jobs-celery-rq.md).

### Supported status UX

Accepted work returns HTTP **202** with `Retry-After`. Prefer **`Poll`** +
`job_status_response` on every host. SSE / WebSocket helpers are FastAPI-flagship and
**experimental** — configure reverse-proxy buffering/timeouts, and prefer polling when
load/proxy backpressure proof is required ([What's ready](guides/whats-ready.md)).

### Inference placement (0.18)

`InferencePolicy` admits/queues work onto the same `JobBackend`. `ModelDemo` /
`InferenceWorkflow` never auto-publish callables as HTTP/MCP endpoints. Cancel maps
accepted requests to `JobBackend.request_cancel`. Details: [Inference](api/INFERENCE.md).

## Security placement

- **Contextual escaping** is default in the renderer.
- **CSRF** runs on unsafe methods when using a built-in profile (`standard` / `strict`).
  Seed tokens with `csrf_token_for_request` (re-exported from `hedron`).
- **`SafeUrl` / `TrustedHtml` / `Secret`** mark trust boundaries in types.
- Application authz and persistence remain your responsibility.
- Job observation over HTTP uses `job_authorized_http` (fail closed for unscoped jobs).

## Assets and builds

- Development may compile scoped CSS and serve package static assets.
- Production expects `hedron build` manifests (`HEDRON_ENV=production`); missing
  manifests refuse to start (`HED-BUILD-0003`).
- Fingerprinted app assets: `/hedron-assets/`. Bundled HTMX: `/hedron-static/`.
- Application developers do not need Node.js.

## Package boundaries

```text
hedron                         FastAPI flagship and beginner API
├── hedron-core                models, components, renderer, registry, inference demos/workflows
├── FastAPI / Starlette        routing, DI, security, ASGI, responses
└── optional integrations      Explorer, data, charts, extras, notebook, mcp, gradio, sample plugins

hedron-flask ──> hedron-core   Flask adapter (Beta Supported; no FastAPI)
hedron-django ─> hedron-core   Django adapter (Beta Supported; Django >=5.2,<6)
hedron-jinja ──> hedron-core   optional .hdj format
hedron-gradio ─> hedron-core   optional Gradio client (Experimental Alpha)
```

`hedron-core` does not import application-framework or transport types. Inference scheduling
(`InferencePolicy`) layers on durable `JobBackend` jobs; `ModelDemo` / `InferenceWorkflow` never
auto-publish callables. Distribution rules: [Project layout](https://github.com/eddiethedean/hedron/blob/main/docs/PROJECT_LAYOUT.md).

## Shared registry

A sealed registry snapshot feeds rendering, routing, OpenAPI, Explorer, assets, CLI,
and diagnostics. Subsystems do not independently rediscover components.

## Architectural invariants

- Rendering never implies route exposure.
- Request props never default to all component props.
- Host-framework security remains authoritative per adapter.
- Rendering contains no hidden I/O.
- Secrets do not enter public metadata, identities, caches, or diagnostics.
- Every inference has an explanation and override.

## See also

[What’s ready](guides/whats-ready.md) · [Compatibility](COMPATIBILITY.md) ·
[Public API coverage](api/COVERAGE.md) · [Configuration](CONFIGURATION.md)

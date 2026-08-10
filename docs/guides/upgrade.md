# Upgrade

**Hedron 0.25.0** — pin `hedron>=0.25.0,<0.26`. Production archetype and extras quarantine
are Verified; polling remains the Supported live-status story. See
[What's ready](whats-ready.md) and [What's new in 0.25](whats-new-0.25.md).

!!! warning "Charts and sample kit on 0.25"

    Historical sections below describe Alpha lines that targeted earlier cores. Upgrade to
    `hedron-charts>=0.1.6,<0.2` and `hedron-sample-kit>=0.1.6,<0.2`; see
    [Compatibility](../COMPATIBILITY.md#charts-and-sample-kit-compatibility-floor).

!!! tip "Jump to your train"

    - **New install?** Use [Build your first app](../getting-started/quickstart.md) — not this page.
    - **Already on 0.24?** Start at [0.24 → 0.25](#upgrade-from-024-025).
    - **Older than 0.22?** Walk the sections below in order, or jump to your starting minor.

## Breaking changes digest (0.24 → 0.25)

| Change | Action |
|---|---|
| Specialty experimental UI moved behind an explicit opt-in | Install `hedron[experimental-ui]` + enable the experimental plugin / `HEDRON_EXPERIMENTAL_UI=1` for CodeEditor / TerminalView / joystick / device; import from `hedron_extras.experimental` |
| `hedron[extras]` no longer registers those experimental surfaces | Update apps that imported them from `hedron_extras` top-level |
| Reference-app production posture | Prefer compose archetype (`HEDRON_ENV=production`, Redis, Explorer off) |

Full step list: [Upgrade from 0.24 → 0.25](#upgrade-from-024-025) below. Older trains:
walk the sections in order, or jump to your starting minor.

## Upgrade from 0.24 → 0.25

If you are already on **0.24.x**, pin coordinated **0.25.0** packages:

```bash
pip install "hedron>=0.25.0,<0.26"
```

1. Re-read [PRODUCTION_ARCHETYPE](../api/PRODUCTION_ARCHETYPE.md) if you deploy multi-worker.
2. If you used CodeEditor / TerminalView / joystick / device, switch to
   `hedron[experimental-ui]` and `hedron_extras.experimental`.
3. Keep polling as the Supported live-status path (unchanged from 0.24).

## Breaking changes digest (0.23 → 0.24)

| Change | Action |
|---|---|
| Live-transport production story locked to **polling** | Keep / adopt `Poll` + `job_status_response`; do not treat `hedron.experimental` SSE/WS as Supported |
| Docs and What’s ready label live helpers **experimental** | Update internal runbooks that assumed Supported SSE |
| No removals from the published Beginner/CRUD `stable` facade | Re-read [STABLE_FACADE](../api/STABLE_FACADE.md) only if you relied on undocumented imports |

Full step list: [Upgrade from 0.23 → 0.24](#upgrade-from-023-024) below.

## Upgrade from 0.23 → 0.24

If you are already on **0.23.x**, pin coordinated **0.24.0** packages (or jump to living
**0.25.0**):

1. Pin `hedron>=0.24.0,<0.25` for a 0.24 freeze, or `hedron>=0.25.0,<0.26` for the living train
   (and matching `hedron-core` / adapters / extras).
2. Keep preferring [polling](live-interaction.md) for production live UX; do not treat
   `hedron.experimental` SSE/WS helpers as Supported
   ([LIVE_DISPOSITION](../api/LIVE_DISPOSITION.md)).
3. Re-run your app suite; read [What's new in 0.24](whats-new-0.24.md) (and
   [What's new in 0.25](whats-new-0.25.md) if jumping to 0.25).
4. Human screen-reader sessions remain Planned / not Supported (carryover from 0.21).

## Upgrade from 0.22 → living 0.25

If you are already on **0.22.x**, pin coordinated **0.25.0** packages (living train includes
0.23 stable-tier expansion and 0.24 polling disposition):

1. Pin `hedron>=0.25.0,<0.26` (and matching `hedron-core` / adapters / extras).
2. Treat the locked Beginner/CRUD facade as compatibility-protected `stable`
   ([STABILITY expanded tier](../api/STABILITY.md#expanded-stable-tier-023) ·
   [STABLE_FACADE](../api/STABLE_FACADE.md)). No API removals from the minimal tier.
3. Prefer polling for production live UX ([LIVE_DISPOSITION](../api/LIVE_DISPOSITION.md)).
4. Re-run your app suite; read [What's new in 0.23](whats-new-0.23.md) and
   [What's new in 0.24](whats-new-0.24.md).
5. Human screen-reader sessions remain Planned / not Supported (carryover from 0.21).

## Upgrade from 0.21 → living 0.25

If you are already on **0.21.x**, pin coordinated **0.25.0** packages, then continue:

1. Pin `hedron>=0.25.0,<0.26` (and matching `hedron-core` / adapters / extras).
2. Prefer `CsrfField` / `Form(hx=Hx(...))` over manual hidden inputs and stringly `hx-*`
   attrs where practical ([CSRF composition](../api/CSRF_COMPOSITION.md)).
3. Apps that own sessions/CSP can pass `SecurityPolicy(csrf=SessionTokenCsrf(...))` or
   `security_headers=SecurityHeadersPolicy(...)` instead of disabling Hedron CSRF/headers.
4. Re-run your app suite; read [What's new in 0.22](whats-new-0.22.md), then apply the
   0.22 → 0.23 / 0.23 → 0.24 notes above.
5. Human screen-reader sessions remain Planned / not Supported (carryover from 0.21).

## Upgrade from 0.20 → 0.21

If you are already on **0.20.x**, pin coordinated **0.25.0** packages, then continue:

1. Pin `hedron>=0.25.0,<0.26` first (or jump directly to `>=0.25.0,<0.26`).
2. Prefer `@action(..., fragment_regions=…)` (or `@component` POST) whenever HTMX sends
   `HX-Target` on mutations.
3. Re-run your app suite; read [What's new in 0.21](whats-new-0.21.md).
4. Treat human screen-reader sessions as not yet Supported — automated AT evidence from
   0.19 remains the Supported AT path (details on [What's ready](whats-ready.md)).

## Upgrade from 0.18 / 0.19 → 0.20

If you are already on **0.18.x** or **0.19.x**, pin coordinated **0.25.0** packages, then
continue:

1. Pin `hedron>=0.25.0,<0.26` (and matching `hedron-core` / adapters / extras).
2. Review production startup gates under `HEDRON_ENV=production` and document any accepted
   risk codes via `HEDRON_SECURITY_RISK_ACCEPTANCE`.
3. Prefer `standard`/`strict` HTMX browser presets; do not rely on `js:` in Python
   `hx-vals` / `hx-headers` unless you explicitly opt in with `allow_htmx_eval`.
4. If you reverse-proxy under a path prefix, set `HEDRON_ROOT_PATH` / ASGI `root_path` and
   expect cookie `Path` + local redirects to follow the mount.
5. Flask/Django: declare `fragment_regions` for fragment targets; expect portable
   `SecurityPolicy` response headers; Flask-Login users prefer `current_user` for AuthSignal.
6. Optional: `hedron new --flask` / `--django` for secure adapter scaffolds.
7. Re-run your app suite; read [What's new in 0.20](whats-new-0.20.md), then apply later
   train notes above.

## Upgrade from 0.17 → 0.18

If you are already on **0.17.x**, pin coordinated **0.18.0** packages and adopt only what you need:

1. Pin `hedron>=0.18.0,<0.19` (and matching `hedron-core` / adapters / extras), then continue to
   the living train with the steps above.
2. For model demos: follow [Model demos](model-demos.md) — `ModelDemo` / `InferenceInterface`
   never auto-publish callables as HTTP or MCP endpoints.
3. Queue inference through `InferencePolicy` onto a durable `JobBackend` for multi-worker;
   in-process queues are **dev-only**.
4. Optional Gradio interop: `hedron[gradio]` is **Alpha / Experimental** — pin and deny-by-default.
5. Re-run your app suite; read [What's new in 0.18](whats-new-0.18.md) for surface inventory.

Skip older archaeology unless you are still on a pre-0.17 line. The sections below are
kept for migrators from 0.8–0.16 (including HDN); current adopters can stop after
upgrading through **0.24 → 0.25** (`hedron>=0.25.0,<0.26`).

---

Existing apps on **0.8.x** / **0.9.x** / **0.10.x** should upgrade through
**0.9** / **0.10** / **0.11** / **0.12** / **0.13** / **0.14** / **0.15** /
**0.16** / **0.17** / **0.18** / **0.19** / **0.20** / **0.21** / **0.22** / **0.23** /
**0.24** to **0.25.0**
(`hedron>=0.25.0,<0.26`).

Version 0.9 intentionally removes HDN and adds optional `hedron-jinja`. There is no compatibility
mode or automatic converter. Stay on 0.8 until every HDN template has been manually rewritten, then
upgrade through **0.9**–**0.24** to **0.25.0**.

## What changed in 0.8

- **Public stability catalog:** every first-party package surface is classified in
  [STABILITY.md](../api/STABILITY.md) (`beta`, `experimental`, `internal`, or `deferred`).
- **Compatibility policy:** numeric deprecation window, semver bump rules by artifact class, and the
  frozen Supported matrix live in [COMPATIBILITY.md](../COMPATIBILITY.md).
- **Django floor:** Supported Django is now `>=5.2,<6` (5.2 LTS). Projects on 5.0/5.1 must upgrade
  Django before claiming Supported adapter status.
- **Django CSRF header:** for portable HTMX clients that send `X-CSRF-Token`, set
  `CSRF_HEADER_NAME = "HTTP_X_CSRF_TOKEN"` in Django settings (reference app does this). Stock
  Django's `X-CSRFToken` remains valid if you keep the default. Form posts may use
  `csrfmiddlewaretoken` or Hedron's portable `csrf_token` field.
- **Hardening evidence:** deeper Flask/Django tests, three-engine browser HTMX suite, performance
  budgets, threat model, SBOM / license / asset audits.
- **HDN end-of-line:** 0.8 is the final release line containing HDN.

## Breaking changes in 0.9

- `hedron_core.hdn`, `compile_hdn`, `format_hdn`, `load_hdn_program`, `run_program`,
  `RenderProgram`, and `HDN_FORMAT_VERSION` are removed.
- `.hdn` files are not discovered, watched, compiled, displayed, or emitted.
- `ComponentMeta.hdn_source` and `BuildManifest.hdn_programs` are removed.
- Build-manifest format 2 rejects 0.8 build artifacts; rebuild after upgrading.
- `hedron eject` emits CSS only.

Install Jinja authoring explicitly with `pip install "hedron[jinja]>=0.25.0,<0.26"` or
`pip install hedron-jinja`. The import namespace is `hedron_jinja`; `.hdj` is the canonical
format-v1 template suffix. Each file begins with the static feature/capability prologue documented
in the [HDJ API](../api/JINJA.md#hdj-format), followed by ordinary Jinja/HTML.

### Manual syntax rewrite

| HDN 0.8 | HDJ 0.9 body |
|---|---|
| `{value}` | `{{ view.value }}` |
| `{#if ready}…{/if}` | `{% if view.ready %}…{% endif %}` |
| `{#for item in items}…{/for}` | `{% for item in view.items %}…{% endfor %}` |
| `<Badge text={label} />` | `{% hedron "Badge" text=view.label %}` |
| component with children | `{% hedron "Card" title=view.title with body %}…{% endhedron %}` |
| `<slot name="footer">…</slot>` | `{% slot "footer" %}…{% endslot %}` |
| `{@html value}` | `{{ view.value|hedron_trusted }}` with a `TrustedHtml` value |

HDN helpers and arbitrary expressions should move into the typed Python view model. Component
aliases are registered explicitly in `HedronJinja`; templates cannot import or enumerate Python
components.

## Historical notes (resolved after 0.11)

| Claim | Decision | Status |
|---|---|---|
| Camera / microphone capture UI | D-045 | Shipped in **0.15** (Supported with policy limits) |
| Django QuerySet DataSource | D-046 | Shipped in **0.11** (Supported) |
| Flask Blueprint / `init_app` | D-041 / D-046 | Shipped in **0.11** (Supported) |
| Django AppConfig convenience | D-041 / D-046 | Shipped in **0.11** (Supported) |
| Celery / RQ `JobBackend` bridges | D-046 | Shipped (Supported optional bridges; shared Redis for multi-worker) |

FastAPI SSE / streaming / WebSocket / preload APIs ship as **experimental**
(`hedron.experimental`); **polling** remains the Supported production fallback on every
host (see [What’s ready](whats-ready.md)). Flask/Django ship capability-labeled live helpers
with the same experimental classification.

## Experimental surfaces

- Plotly / Altair **full interactive** chart runtimes remain **experimental** until offline pin and
  browser evidence promote them. Matplotlib static SVG remains the conservative default.
- `hedron-sample-kit` remains an Alpha/experimental plugin sample.

## Upgrade steps (from 0.8 HDN)

1. On 0.8, inventory every `.hdn` file and direct HDN API use.
2. Rewrite each template as typed Python or a Jinja template and add explicit component bindings.
3. Delete `.hdn` source and any code reading HDN build artifacts.
4. Pin coordinated `0.9.0` packages and add `hedron-jinja` only where templates are used.
5. Delete old build output, rebuild format-2 manifests, and run the Jinja and application suites.
6. Work through the progressive HDJ examples under
   [`examples/hdj-progressive`](https://github.com/eddiethedean/hedron/tree/main/examples/hdj-progressive)
   before migrating production templates.
7. Re-run security, HTMX, and adapter suites; for production, exercise Chromium/Firefox/WebKit
   against critical flows when you consume HTMX history, OOB, or extensions.
8. Read [STABILITY.md](../api/STABILITY.md) before depending on unmarked or private APIs.
9. Continue through intermediate lines to **0.18.0** (see phase notes below).

## 0.10 live interaction (published)

Phase 0.10 ships SSE, focused streaming, WebSocket channels, Chat/Dialog, and opt-in navigation
preload (RFC-0032). Each phase publishes its own upgrade notes and proves clean install, upgrade
from supported prior lines, deployment, and rollback from built/published artifacts. See
[RELEASE.md](https://github.com/eddiethedean/hedron/blob/main/docs/RELEASE.md) and the roadmap.

### 0.9 → 0.10

1. Upgrade to the coordinated `0.10.x` train.
2. Keep polling job-status UIs; optionally mount SSE observation via `job_status_sse_response`
   and include `/hedron-static/ext/sse.js` when using `hx-ext="sse"`.
3. Use `Dialog` / `ChatMessage` / `ChatInput` for new interaction surfaces; do not treat live
   transports as a correctness dependency.
4. Enable navigation preload only through an explicit `NavigationPreloadPolicy(enabled=True)`.
5. Prefer `HedronJinja.two_phase_stream()` over raw `Template.stream()` for HDJ streaming.

## 0.11 native Flask/Django depth (published)

Phase 0.11 ships Flask Blueprint/`init_app`, Django `AppConfig`, forms bridge, bounded
`DjangoQuerySetDataSource`, portable adapter test harnesses, HDJ dynamic manifests/CSP
inventory, Celery/RQ `JobBackend` bridges, and capability-labeled Flask/Django live helpers.

### Checklist: 0.10 → 0.11

1. Pin and upgrade to the coordinated `0.11.0` train (`hedron`, adapters, extras together).
2. Flask apps may adopt `HedronFlask().init_app(app)` and `HedronBlueprint` without changing the
   constructor-owned path.
3. Add `hedron_django.apps.HedronDjangoConfig` to `INSTALLED_APPS` for system checks.
4. Prefer `DjangoQuerySetDataSource(authorized_qs, ...)` over ad-hoc QuerySet materialization;
   never pass an unauthorized base QuerySet.
5. Use `form_to_nodes` / `validation_interaction` for Django forms ↔ Hedron HTMX error parity;
   saving remains in the view.
6. Optional: wire `CeleryJobBackend` / `RQJobBackend` for durable jobs; keep polling as the
   Supported status transport on buffering proxies.
7. Re-read [What's ready](whats-ready.md) for live-transport caveats (unchanged: prefer polling
   until you have your own SSE/WS ops proof).

Narrative: [What's new in 0.11](whats-new-0.11.md).

## 0.12 data and visualization scale (published)

Phase 0.12 ships the shared column catalog, typed grid/chart events, saved views,
`TransformPlan`, advanced DataEditor (formulas, pivots, trees, collab, spreadsheet I/O),
AG Grid Community client/infinite, Dask/Snowflake sources, beginner Area/Bar/Scatter charts,
Plotly events/annotations, optional adapters with offline runtime pins, and HDJ
`hedron.data` / `hedron.charts` provider parity (D-047).

### Checklist: 0.11 → 0.12

1. Pin and upgrade to the coordinated `0.12.0` Beta train (`hedron`, adapters, extras together).
   Alpha packages `hedron-charts` / `hedron-sample-kit` remain on `0.1.x`.
2. Prefer `hedron[dev]` / `hedron[jinja]` extras (then `>=0.12,<0.13`) with matching packages.
3. Adopt `TransformPlan` / saved views / column catalog APIs for new data surfaces; keep app-owned
   authz around Dask/Snowflake statements (SELECT/WITH only).
4. Treat AG Grid as Community client + infinite only; Tabulator remains the default editor host.
5. Charts remain Alpha: pin `hedron-charts` and prefer offline pinned runtimes over CDNs.
6. Re-read [What's ready](whats-ready.md) and [What's new in 0.12](whats-new-0.12.md).

## 0.13 advanced async and observability (published)

Phase 0.13 ships optional component `prepare()`, adaptive concurrency, optional OpenTelemetry
tracing (`hedron[otel]`), HDJ async I/O budgets, `SecurityAuditSink`, Redis-durable Celery/RQ
status, live-transport claim honesty, and a complete `HED-*` catalog.

### Checklist: 0.12 → 0.13

1. Pin and upgrade to the coordinated `0.13.0` Beta train (`hedron`, adapters, extras together).
2. Prefer `hedron[dev]` / `hedron[jinja]` extras (then `>=0.13,<0.14`) with matching packages.
3. Optional: implement `async def prepare(self, ctx)` on components that need request-owned I/O
   before sync `render()`; keep constructors free of hidden I/O.
4. Celery/RQ bridges now **require** `redis_client=` for durable multi-worker status — pass a shared
   Redis client or stop claiming durability.
5. Optional: `configure_tracing(enabled=True)` / `hedron[otel]`; disable anytime without changing
   component semantics.
6. Optional: `set_security_audit_sink(...)` for framework-boundary security events.
7. Re-read [What's ready](whats-ready.md): SSE/WS/stream/preload remain experimental; polling is the
   Supported production fallback.

## 0.14 portable runtimes and acceleration (published)

Phase 0.14 ships the language-neutral `hedron-conformance` kit, experimental Java/Node runtimes,
optional `hedron-native` HTML-escape acceleration with pure-Python fallback, and HDJ
instrumentation (`HDJ-DEF-014`) under D-048.

### Checklist: 0.13 → 0.14

1. Pin and upgrade to the coordinated `0.14.0` Beta train (`hedron`, adapters, extras together).
   Alpha packages `hedron-charts` / `hedron-sample-kit` / `hedron-native` remain on `0.1.x`.
2. Optional: `pip install "hedron[conformance]>=0.25.0,<0.26"` for the fixture kit / `hedron conformance` CLI.
3. Optional: `pip install "hedron[native]>=0.1.0,<0.2"` for Rust accel; absence must not change semantics
   (`hedron accel-status`).
4. HDJ authors: review loop/macro budgets, contracted extensions, and portable checker fixtures
   (`HDJ-DEF-014`).
5. Re-read [What's ready](whats-ready.md) and [What's new in 0.14](whats-new-0.14.md).

## 0.15 data-app surface completeness (Published)

Phase 0.15 ships the remaining high-value Streamlit data-app surface and accepted NiceGUI-adjacent
controls without whole-script reruns or Vue/outbox mutation. See
[Streamlit migration matrix](streamlit-migration-matrix.md) and
[NiceGUI migration](nicegui-migration.md).

### Checklist: 0.14 → 0.15

1. Pin and upgrade to the coordinated `0.15.0` Beta train (`hedron`, adapters, extras together).
   Alpha packages `hedron-charts` / `hedron-sample-kit` / `hedron-native` remain on `0.1.x`.
2. Prefer `region` / `@fragment` / `swap` for new HTMX authoring; fail-closed
   `fragment_regions` authorization is unchanged.
3. Adopt typed controls (`DateInput`, `RangeInput`, …), surface chrome, `Map`, and media helpers
   where you previously used custom HTML or third-party widgets.
4. Optional: OIDC / session hardening helpers and the named connection registry — host sessions and
   DI remain authoritative; do not treat helpers as an IdP or global service locator.
5. Prefer `AppScenario` and HTMX testing asserts (#22–#26) for application-flow coverage; they
   exercise ordinary HTTP, not Streamlit-style reruns.
6. Re-read [What's ready](whats-ready.md) and the [upgrade](upgrade.md) Streamlit/NiceGUI guides.

## 0.16 curated extras and analysis workbenches (Published)

Phase 0.16 adds optional `hedron-extras` without expanding the core runtime. Specialty surfaces
remain **Experimental**. CodeEditor is a CSP-safe host stub (no pinned CodeMirror 6 bundle).

### Checklist: 0.15 → 0.16

1. Pin and upgrade to the coordinated `0.16.0` Beta train (`hedron`, adapters, `hedron-extras`).
   Alpha packages remain on `0.1.x` with `hedron-core>=0.16.0,<0.17`.
2. Install extras only when needed: `pip install "hedron[extras]>=0.25.0,<0.26"`.
3. Prefer workbench components that emit bounded plans/actions over implicit callables.
4. Do not market TerminalView / joystick / device bridges as Supported production features.
5. Re-read [What's new in 0.16](whats-new-0.16.md) and [What's ready](whats-ready.md).

## 0.17 reactive dashboards and agent interfaces (Published)

Phase 0.17 adds page-local interaction graphs, bounded patches with mandatory full-fragment
fallback, cross-filter composition, HTMX shell authoring primitives, and optional Alpha
notebook/MCP packages. Live transports remain **experimental**. Notebook preview and MCP are
**Experimental** — not Supported production by default.

### Checklist: 0.16 → 0.17

1. Pin and upgrade to the coordinated `0.17.0` Beta train (`hedron`, adapters, extras).
   Alpha packages remain on `0.1.x` with `hedron-core>=0.17.0,<0.18`.
2. Prefer `DashboardBinding` / `InteractionGraph` over ad-hoc multi-region wiring; registration
   fails closed on cycles and duplicate writers.
3. Use `PropertyPatch` / `CollectionPatch` only with declared schemas; always keep a full-fragment
   fallback path.
4. Adopt shell primitives (`NavLink`, `OobHost`, `AppShell`/`MainPanel`) and public
   `render_interaction` when converting `InteractionResult` outside route internals.
5. Install Alpha extras only when needed: `pip install "hedron[notebook]>=0.1.0,<0.2"` /
   `"hedron[mcp]>=0.1.0,<0.2"`. Keep MCP disabled/empty by default.
6. Re-read [What's new in 0.17](whats-new-0.17.md), [Dash migration](dash-migration.md), and
   [NiceGUI migration](nicegui-migration.md).

## 0.18 model demos and inference workflows (Published)

Phase 0.18 adds fail-closed `ModelDemo` / `InferenceInterface`, `ExampleSet`, presentation
builtins, governed `PredictionFeedback`, `InferencePolicy` over `JobBackend`,
`InteractionRecorder`, versioned `InferenceWorkflow`, and optional Alpha `hedron-gradio`.
Gradio interop is **Experimental** — pin Alpha and expect churn. Live transports remain
**experimental**; prefer polling.

### Checklist: 0.17 → 0.18

1. Pin and upgrade to the coordinated `0.18.0` Beta train (`hedron`, adapters, extras).
   Alpha packages remain on `0.1.x` with `hedron-core>=0.18.0,<0.19` for that train
   (0.20 pins are `>=0.20.0,<0.21`; living train pins are `>=0.25.0,<0.26`).
2. Build demos only from `ActionRegistry` / `RegisteredCallableAdapter` — bare callables fail closed.
3. Wire `InferencePolicy` concurrency groups and cancel through durable `JobBackend`; do not use
   `InProcessInferenceQueue` as a production durability promise.
4. Enable `PredictionFeedback` only after explicit consent; pass `principal=` when
   `authorization_required` is true; never treat feedback as ground truth.
5. Use `InferenceWorkflow.run(..., registry=...)` for ACTION/MODEL execution; graph JSON cannot
   host code or auto-publish HTTP/MCP endpoints.
6. Optional: `pip install "hedron[gradio]>=0.1.0,<0.2"` for client discovery/jobs; keep adapters disabled by
   default. See [Gradio migration](gradio-migration.md) and [Model demos](model-demos.md).
7. Re-read [What's new in 0.18](whats-new-0.18.md) and [What's ready](whats-ready.md).

## Deprecation tooling

There is no code-rewriting migration CLI. Follow the semantic table above and keep the application
on 0.8 until the rewrite is complete.

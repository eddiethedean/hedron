# Upgrade

Current train: **0.15.0** (implemented pending cut). From 0.14: AppScenario / HTMX testing
helpers, `region`/`@fragment`/`swap`, typed controls and surface chrome, media Range/downloads,
Map/GeoJSON, BrowserContext/Storage, Math/IFrame, OIDC/session helpers, and the connection
registry. See [What's ready](whats-ready.md).


Hedron publishes coordinated Beta trains. Existing apps on **0.8.x** / **0.9.x** / **0.10.x** should
upgrade through **0.9** / **0.10** / **0.11** / **0.12** / **0.13** / **0.14** to the **0.15.0** train for
data-app surface completeness (plus prior portable conformance / optional native acceleration).

Version 0.9 intentionally removes HDN and adds optional `hedron-jinja`. There is no compatibility
mode or automatic converter. Stay on 0.8 until every HDN template has been manually rewritten, then
upgrade through **0.9** / **0.10** / **0.11** / **0.12** / **0.13** / **0.14** to the **0.15.0** train.

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

Install Jinja authoring explicitly with `pip install "hedron[jinja]"` or
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

## Still Deferred (after 0.11)

| Claim | Decision | Guidance |
|---|---|---|
| Camera / microphone capture UI | D-045 | Remains phase **0.15**. |

FastAPI SSE / streaming / WebSocket / preload APIs ship as **experimental**
(`hedron.experimental`); **polling** remains the Supported production fallback on every
host (see [What’s ready](whats-ready.md)). Flask/Django ship capability-labeled live helpers
with the same experimental classification.

## Experimental surfaces

- Plotly / Altair **full interactive** chart runtimes remain **experimental** until offline pin and
  browser evidence promote them. Matplotlib static SVG remains the conservative default.
- `hedron-sample-kit` remains an Alpha/experimental plugin sample.

## Upgrade steps

1. On 0.8, inventory every `.hdn` file and direct HDN API use.
2. Rewrite each template as typed Python or a Jinja template and add explicit component bindings.
3. Delete `.hdn` source and any code reading HDN build artifacts.
4. Pin the coordinated `0.9.0` train and add `hedron-jinja` only where templates are used.
5. Delete old build output, rebuild format-2 manifests, and run the Jinja and application suites.
6. Work through the progressive HDJ examples under
   [`examples/hdj-progressive`](https://github.com/eddiethedean/hedron/tree/main/examples/hdj-progressive)
   before migrating production templates.
7. Re-run security, HTMX, and adapter suites; for production, exercise Chromium/Firefox/WebKit
   against critical flows when you consume HTMX history, OOB, or extensions.
8. Read [STABILITY.md](../api/STABILITY.md) before depending on unmarked or private APIs.

## 0.10 live interaction (published)

Phase 0.10 ships SSE, focused streaming, WebSocket channels, Chat/Dialog, and opt-in navigation
preload (RFC-0032). Each phase publishes its own upgrade notes and proves clean install, upgrade
from supported prior trains, deployment, and rollback from built/published artifacts. See
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
2. Optional: `pip install "hedron[conformance]"` for the fixture kit / `hedron conformance` CLI.
3. Optional: `pip install "hedron[native]"` for Rust accel; absence must not change semantics
   (`hedron accel-status`).
4. HDJ authors: review loop/macro budgets, contracted extensions, and portable checker fixtures
   (`HDJ-DEF-014`).
5. Re-read [What's ready](whats-ready.md) and [What's new in 0.14](whats-new-0.14.md).

## 0.15 data-app surface completeness (implemented pending cut)

Phase 0.15 ships the remaining high-value Streamlit data-app surface and accepted NiceGUI-adjacent
controls without whole-script reruns or Vue/outbox mutation. See
[Streamlit migration matrix](streamlit-migration-matrix.md) and
[NiceGUI migration](nicegui-migration.md).

### Checklist: 0.14 → 0.15

1. Pin and upgrade to the coordinated `0.15.0` Beta train (`hedron`, adapters, extras together).
   Alpha packages `hedron-charts` / `hedron-sample-kit` / `hedron-native` remain on `0.1.x`
   (compatible with `hedron-core>=0.15.0,<0.16`).
2. Prefer `region` / `@fragment` / `swap` for new HTMX authoring; fail-closed
   `fragment_regions` authorization is unchanged.
3. Adopt typed controls (`DateInput`, `RangeInput`, …), surface chrome, `Map`, and media helpers
   where you previously used custom HTML or third-party widgets.
4. Optional: OIDC / session hardening helpers and the named connection registry — host sessions and
   DI remain authoritative; do not treat helpers as an IdP or global service locator.
5. Prefer `AppScenario` and HTMX testing asserts (#22–#26) for application-flow coverage; they
   exercise ordinary HTTP, not Streamlit-style reruns.
6. Re-read [What's ready](whats-ready.md) and the [upgrade](upgrade.md) Streamlit/NiceGUI guides.

## Deprecation tooling

There is no code-rewriting migration CLI. Follow the semantic table above and keep the application
on 0.8 until the rewrite is complete.

# Upgrade guide (0.8 → 0.9 authoring break)

Version 0.9 intentionally removes HDN and adds optional `hedron-jinja`. There is no compatibility
mode or automatic converter. Stay on 0.8 until every HDN template has been manually rewritten.

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

## Still Deferred (unchanged)

| Claim | Decision | Guidance |
|---|---|---|
| Django QuerySet DataSource | D-036 | Bridge QuerySets in application code; do not rely on a first-party portable contract. |
| HTMX SSE live transport | D-037 / D-044 | Official SSE is Supported in 0.10; bounded polling remains the Supported fallback. |

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

## Toward 0.10 and later phases

Phase 0.10 adds SSE, focused streaming, WebSocket channels, Chat/Dialog, and opt-in navigation
preload (RFC-0032). Native Flask/Django depth moves to 0.11. Each phase publishes its own
upgrade notes and proves clean install, upgrade from supported prior trains, deployment, and
rollback from built/published artifacts. See [RELEASE.md](../RELEASE.md) and the roadmap.

### 0.9 → 0.10

1. Upgrade to the coordinated `0.10.0` train.
2. Keep polling job-status UIs; optionally mount SSE observation via `job_status_sse_response`
   and include `/hedron-static/ext/sse.js` when using `hx-ext="sse"`.
3. Use `Dialog` / `ChatMessage` / `ChatInput` for new interaction surfaces; do not treat live
   transports as a correctness dependency.
4. Enable navigation preload only through an explicit `NavigationPreloadPolicy(enabled=True)`.
5. Prefer `HedronJinja.two_phase_stream()` over raw `Template.stream()` for HDJ streaming.

## Deprecation tooling

There is no code-rewriting migration CLI. Follow the semantic table above and keep the application
on 0.8 until the rewrite is complete.

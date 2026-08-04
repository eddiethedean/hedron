# Upgrade guide (0.7 → 0.8 and later capability phases)

This guide covers the `0.8.0` hardening/compatibility baseline and how later `0.x` capability
phases declare migration impact. No 1.0 freeze is scheduled.

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
- **HDN migration:** existing experimental templates use `template.hdn`, but D-040/RFC-0031 select
  an optional Jinja replacement and schedule HDN deprecation in 0.11, default-discovery removal in
  0.12, and runtime removal in 0.13. Do not create new HDN dependencies. Current discovery,
  `hedron eject`, and the development watcher retain the legacy extension temporarily.

## Still Deferred (unchanged)

| Claim | Decision | Guidance |
|---|---|---|
| Django QuerySet DataSource | D-036 | Bridge QuerySets in application code; do not rely on a first-party portable contract. |
| HTMX SSE live transport | D-037 | Use bounded polling for job status (`JobBackend` + 202 responses). |

## Experimental surfaces

- Plotly / Altair **full interactive** chart runtimes remain **experimental** until offline pin and
  browser evidence promote them. Matplotlib static SVG remains the conservative default.
- `hedron-sample-kit` remains an Alpha/experimental plugin sample.

## Upgrade steps

1. Pin the coordinated train: `hedron==0.8.0` (and matching `hedron-core`, extras, adapters).
2. If you use `hedron-django`, ensure Django `>=5.2,<6`.
3. Run `hedron check` and review freeze-boundary informational diagnostics (Deferred SSE/QuerySet,
   experimental chart runtimes, Django floor).
4. Inventory existing `template.hdn` usage and keep it on the legacy filename for now. Prefer Python
   for new components; do not treat current imports, expressions, or artifacts as replacement APIs.
5. Re-run your security, HTMX, and adapter suites; for production, exercise Chromium/Firefox/WebKit
   against critical flows when you consume HTMX history, OOB, or extensions.
6. Read [STABILITY.md](../api/STABILITY.md) before depending on unmarked or private APIs.

## Toward 0.9 and later phases

Phase 0.9 owns native Flask/Django application integration and the bounded QuerySet source; phase
0.10 owns SSE, WebSocket, focused streaming, and navigation preload. Each phase publishes its own
upgrade notes and proves clean install, upgrade from supported prior trains, deployment, and
rollback from built/published artifacts. See [RELEASE.md](../RELEASE.md) and the roadmap.

## Deprecation tooling

`hedron check` emits informational diagnostics for freeze-boundary compatibility notes. There is no
code-rewriting migrate CLI in 0.8; follow this guide and changelog entries for required changes.

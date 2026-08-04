# Upgrade guide (0.7 → 0.8 and toward 1.0)

This guide covers the feature-frozen `0.8.0` train and the path to published `1.0.0rcN` artifacts.
Phase 0.8 adds **no** new subsystems, adapters, or transports.

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
- **HDN source extension:** preferred component template filename is `template.hdx` (JSX-familiar).
  `template.hdn` remains a discoverable compatibility fallback; `hedron eject` and new overrides
  write `.hdx`. Rename existing `template.hdn` files when convenient.

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
4. If you author HDN templates, prefer `template.hdx`. Legacy `template.hdn` still works; when both
   exist in a folder, discovery uses `.hdx` and logs a warning.
5. Re-run your security, HTMX, and adapter suites; for production, exercise Chromium/Firefox/WebKit
   against critical flows when you consume HTMX history, OOB, or extensions.
6. Read [STABILITY.md](../api/STABILITY.md) before depending on unmarked or private APIs.

## Toward `1.0.0rcN`

After `v0.8.0` is published, install only published RC wheels for clean-install, upgrade-from-0.8,
deployment, and rollback rehearsal. Stable `v1.0.0` differs from the final RC only by approved
version metadata. See [RELEASE.md](../RELEASE.md).

## Deprecation tooling

`hedron check` emits informational diagnostics for freeze-boundary compatibility notes. There is no
code-rewriting migrate CLI in 0.8; follow this guide and changelog entries for required changes.

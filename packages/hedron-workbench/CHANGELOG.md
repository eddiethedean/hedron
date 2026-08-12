# Changelog

## [0.29.0] — 2026-08-11

### Added

- Initial Beta release of `hedron-workbench`: Posit Workbench / RStudio Server
  deployment adapter (D-057 / RFC-0062). Pre-import launcher, `workbenchify`
  wrap-once middleware, pure resolver, and `check` / `--dry-run` diagnostics.
  Behavior baseline is observed fastapi-workbench 0.3.4 (MIT attribution; no
  runtime dependency).
- Added `HedronWorkbench`, a `Hedron` subclass that consumes pre-import launcher
  state, normalizes Workbench paths exactly once, and remains an ordinary Hedron
  app when Workbench is inactive.
- Hardened mount/public-URL/port/worker/proxy validation, bounded discovery
  output, structured redaction, explicit external-bind opt-in, and fail-closed
  malformed request targets.
- Added `external_url()` / `external_url_for()` for email invites and callbacks,
  with structured query encoding, route reversal, loopback-origin rejection,
  and strict Posit Connect runtime/header/ASGI-root corroboration.
- Added digest-pinned licensed Docker acceptance deployments for Posit Workbench
  and Posit Connect, including pages, fragments, CSRF, cookies, assets, OpenAPI,
  redirects, encoded-target isolation, WebSockets, secret isolation, invite
  URLs, and ordinary-Hedron parity outside both platforms.

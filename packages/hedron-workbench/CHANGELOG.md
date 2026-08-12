# Changelog

## [0.30.0] — 2026-08-12

- Coordinated `0.30.0` train; `hedron-workbench` depends on `fastapi-workbench` 1.0.0 (phase 0.30 / D-058).


## [0.29.0] — 2026-08-11

### Added

- Automatic render-time mount adaptation for Hedron URL attributes plus a
  browser runtime for fetch, EventSource, and WebSocket paths.
- Request-aware safe redirect/HTMX header rewriting and Hedron-owned cookie Path
  repair for ASGI mounts that arrive after construction.
- Separate browser-session and durable URL APIs, deployment capabilities,
  background-safe external-base capture, topology profiles, and `doctor --live`.
- Parent-side discovery followed by inherited-socket Uvicorn reload/workers.
- A complete Uvicorn runtime, including WebSocket and reload dependencies, in
  the default Workbench installation.
- Posit Connect's asymmetric proxy contract: emit owned cookies for one outer
  path rebase while continuing to mount redirects inside Hedron.
- Native-amd64 authenticated Workbench proxy E2E and expanded Connect runtime
  cookie/link acceptance coverage.
- Initial Beta release of `hedron-workbench`: Posit Workbench / RStudio Server
  deployment adapter (D-057 / RFC-0062). Pre-import launcher, `workbenchify`
  wrap-once middleware, pure resolver, and `check` / `--dry-run` diagnostics.
  Behavior baseline is observed fastapi-workbench 0.3.4 (MIT attribution; no
  runtime dependency).
- Added `HedronWorkbench`, a `Hedron` subclass that consumes pre-import launcher
  state, normalizes Workbench paths exactly once, and remains an ordinary Hedron
  app when Workbench is inactive.
- Added `external_url()` / `external_url_for()` for email invites and callbacks,
  with structured query encoding, route reversal, loopback-origin rejection,
  and strict Posit Connect runtime/header/ASGI-root corroboration.
- Added digest-pinned licensed Docker acceptance deployments for Posit Workbench
  and Posit Connect, including pages, fragments, CSRF, cookies, assets, OpenAPI,
  redirects, encoded-target isolation, WebSockets, secret isolation, invite
  URLs, and ordinary-Hedron parity outside both platforms.

### Security

- Bound encoded absolute request targets to canonical expected origins; reject
  credentials, fragments, malformed ports, and unknown hosts.
- Reject rserver-url query strings and invalid UTF-8, canonicalize IPv6 origins,
  accept bounded proxy CIDRs, and clear stale launcher handoff state.
- Hardened mount/public-URL/port/worker/proxy validation, bounded discovery
  output, structured redaction, explicit external-bind opt-in, and fail-closed
  malformed request targets.

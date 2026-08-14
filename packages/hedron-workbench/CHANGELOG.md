## [0.37.0]

- Coordinated train cut for phase 0.37 (D-065).

## [0.36.0] — 2026-08-13

- Coordinated Beta train cut for Web Component ABI foundation (D-064 / RFC-0060).

## [0.35.0] — 2026-08-13

### Added

- Coordinated Beta train cut for whole-fleet production-grade closure (D-063 / RFC-0068).

## [0.34.0] — 2026-08-13

### Added

- Coordinated Beta train cut for production-grade Gradio client interop (D-062 / RFC-0067).

# Changelog

## [0.33.0] — 2026-08-13

- Coordinated train bump for phase 0.33 (`hedron-posit` unified Posit adapter; D-061 / RFC-0066).

## [0.32.0] — 2026-08-12

- Coordinated train bump for phase 0.32 MCP production-grade graduation.

### Fixed

- Skip `rserver-url` discovery in `run_target` / `check --discover` / `doctor --live`
  when `UVICORN_ROOT_PATH` or resolved-mount env already supplies the mount
  (parity with fastapi-workbench #144; #159).

### Security

- Raise the Starlette floor to ``>=1.3.1`` (aligned with ``fastapi-workbench``)
  so installs resolve patched releases for known Starlette advisories.

## [0.31.0] — 2026-08-12

- Coordinated `0.31.0` train: tooling-grade conformance/sim/notebook/sample-kit/Node+Java evaluators and `hedron migrate streamlit` (D-059 / RFC-0064 / RFC-0061).

## [0.30.0] — 2026-08-12

- Coordinated `0.30.0` train; `hedron-workbench` depends on `fastapi-workbench` 1.0.0 (phase 0.30 / D-058).
- Inherits `fastapi-workbench` 1.0.0 path-security and mount-hint runner fixes (#142, #144).


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

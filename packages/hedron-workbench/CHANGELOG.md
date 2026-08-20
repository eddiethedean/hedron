# Changelog

## [0.53.0] — 2026-08-20

### Added

- Coordinated train tip `0.53.0` (in-tree Published; tag/PyPI deferred).
- Application DX contracts (RFC-0080 / D-091 / D-092): assets, diagnostics, routes,
  workflows, testgen, theming, discovery, and fleet doctor.

## [0.52.0] — 2026-08-20

### Changed
- Coordinated train tip `0.52.0` (in-tree Published; tag/PyPI deferred).
- Phase 0.52 conformance authority + Posit lifecycle (RFC-0079 / D-089 / D-090; #522).

## [0.51.2] — 2026-08-20

### Changed
- Coordinated train tip `0.51.2`.

### Fixed
- See flagship `hedron` changelog for the full 0.51.2 quality/typing list.

## [0.51.1] — 2026-08-20

### Changed
- Coordinated train tip `0.51.1` (in-tree patch; tag/PyPI deferred).

### Fixed
- See flagship `hedron` changelog for the full 0.51.1 bugfix list.

## [0.51.0] — 2026-08-19

### Changed
- Coordinated train tip `0.51.0` (in-tree; tag/PyPI deferred).

## [0.50.3] — 2026-08-19

### Changed
- Coordinated train tip `0.50.3`.

### Fixed
- HTMX `@command` and compiled refresh/patch responses stay fail-closed for undeclared targets.
- Tabular normalize, secret columns, draft-transfer names, and secret-like redaction no longer leak or false-match.
- Data/chart/patch/CSS/image/collab correctness (see tests/unit/test_bugfix_0503.py).

## [0.50.2] — 2026-08-19

### Changed
- Coordinated train tip `0.50.2` (in-tree patch; tag/PyPI deferred).

## [0.50.1] — 2026-08-18

### Changed
- Coordinated train tip `0.50.1`.

## [0.50.0] — 2026-08-18

### Changed
- Coordinated train tip `0.50.0` (in-tree cut; tag/PyPI deferred).

### Added
- Explorer architecture services/views split, ExplorerProvider v1, query pagination,
  diffs, headless CLI parity, bounded lab, and HTMX authoring primitives (#496–#500, #502, #503).

## [0.49.1] — 2026-08-18

### Changed
- Coordinated train tip `0.49.1` (in-tree patch; tag/PyPI deferred).

## [0.49.0] — 2026-08-17

### Added
- Phase 0.49 FastAPI/Pydantic convergence (D-081 / D-084 / RFC-0076).

### Changed
- Coordinated train tip `0.49.0` (in-tree cut; tag/PyPI deferred).


## [0.48.0] — 2026-08-17

### Added
- Phase 0.48 first-class HTMX extension integration (D-080 / D-083 / RFC-0075).

### Changed
- Coordinated train tip `0.48.0` (in-tree cut; tag/PyPI deferred).

## [0.47.0] — 2026-08-17

### Added
- Phase 0.47 first-class maps (`hedron-maps` 0.1.0) on the coordinated train (D-078 / D-082 / RFC-0074).

### Changed
- Coordinated train tip `0.47.0` (in-tree cut; tag/PyPI deferred).

## [0.46.0] — 2026-08-16

### Added
- Coordinated train tip with catalog-backed workbench inspection.

### Changed
- Coordinated train tip `0.46.0`.


## [0.45.0] — 2026-08-16

### Added
- Phase 0.45 production interactions.json validation; fastapi-workbench stays compatibility_only.

### Changed
- Coordinated train tip `0.45.0` (in-tree cut; tag/PyPI deferred).

## [0.44.0] — 2026-08-16

### Added
- Phase 0.44 type-driven authoring (D-072 / D-076 / RFC-0071).

### Changed
- Coordinated train tip `0.44.0` (in-tree cut; tag/PyPI deferred).


## [0.43.0] — 2026-08-16

### Added
- Phase 0.43 refreshable views, command handles, and typed updates (D-071 / RFC-0070).

### Changed
- Coordinated train tip `0.43.0` (in-tree cut; tag/PyPI deferred).

## [0.42.0] — 2026-08-14

### Added
- Phase 0.42 production-grade Web Component platform graduation (D-070).

### Changed
- Coordinated train tip `0.42.0` (in-tree cut; tag/PyPI deferred).

## [0.41.0] — 2026-08-15

- Phase 0.41 browser composition, bounded draft transfer, navigation, tracing, failure isolation, and regression closure (D-069).

## [0.40.0] — 2026-08-14

### Added
- Phase 0.40 authoring kit, metadata parity, React migration matrix, and remediation packet (D-068).

## [0.39.0] — 2026-08-14

### Added
- Phase 0.39 rich data ABI, OptimisticMutation, chartlink, and remediation packet (D-067).

## [0.38.0] — 2026-08-14

- Phase 0.38 high-fidelity charts / train alignment (D-066 / RFC-0069).


## [0.37.0] — 2026-08-14

- Coordinated train cut for phase 0.37 (D-065).

## [0.36.0] — 2026-08-13

- Coordinated Beta train cut for Web Component ABI foundation (D-064 / RFC-0060).

## [0.35.0] — 2026-08-13

### Added

- Coordinated Beta train cut for whole-fleet production-grade closure (D-063 / RFC-0068).

## [0.34.0] — 2026-08-13

### Added

- Coordinated Beta train cut for production-grade Gradio client interop (D-062 / RFC-0067).

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

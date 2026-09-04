# Changelog

## [1.0.11] — 2026-09-04

### Fixed
- Prefer an explicit public-base mount over stale `UVICORN_ROOT_PATH` data while preserving
  path-only runtime redirect semantics when the public base supplies only an origin.
- Keep non-interactive Workbench jobs and resolved launcher source metadata on their existing
  safe paths during public-base resolution.

### Tests
- Add regression coverage for public-base precedence, origin-only discovery, job suppression,
  source replay, and compatibility-warning deduplication.

## [1.0.10] — 2026-09-02

### Fixed
- Merge launcher-discovered mounts, origins, modes, redirect policy, and owned cookies into
  applications that called `workbenchify()` before launcher discovery.
- Canonicalize proxy-prefixed ASGI roots when an upstream proxy has already stripped the request
  path and the remaining root exactly matches the resolved Workbench session mount.
- Rebase quoted owned-cookie `Path` attributes, including the Posit Connect outer-proxy handoff.
- Make `mode="off"` a complete pass-through for response headers and cookies as well as scopes.
- Preserve the resolved public origin when the launcher receives an isolated environment mapping.

### Tests
- Add a production-shaped FastAPI matrix covering Workbench ingress variants, static files,
  OpenAPI, generated URLs, sessions, redirects, HTMX headers, encoded values, and WebSockets.

## [1.0.9] — 2026-09-02

### Fixed
- Canonicalize valid trailing-slash ASGI root paths without promoting malformed roots into
  trusted mounts.
- Canonicalize internal `/proxy/<port>` prefixes in path and full-URL `UVICORN_ROOT_PATH`
  values.
- Preserve path-only `UVICORN_ROOT_PATH` discovery semantics so legacy proxy redirects remain
  relative and mount-safe.

## [1.0.8] — 2026-09-02

### Fixed
- Keep path-only redirects to same-directory and ancestor canonical routes slash-free,
  avoiding a second mount-unsafe Starlette redirect (#883).

## [1.0.7] — 2026-09-02

### Added
- Add an explicit `run --discover` launcher option for bind-then-`rserver-url`
  discovery when Workbench omits `RS_SERVER_URL`.
- Honor explicit discovery in `check` and `doctor --live` without requiring
  `RS_SERVER_URL`.

## [1.0.6] — 2026-09-02

### Fixed
- Emit relative browser `Location` redirects when Workbench mount discovery returns
  only a path, so the legacy `/proxy/<port>/` entry point does not double-prefix them.

## [1.0.5] — 2026-09-01

### Fixed
- Resolve `module:attribute` application targets from the current project directory when
  launched through the console script, matching Uvicorn's documented import behavior.

## [1.0.4] — 2026-08-31

### Security
- Reject malformed bracketed request targets and redact encoded sensitive query keys from
  malformed URLs before including them in diagnostics.

## [1.0.3] — 2026-08-31

### Security
- Harden proxy trust, request-target validation, diagnostics redaction, and launcher state
  handoff across Workbench deployments.

### Fixed
- Export resolved launcher state through every mutable process environment, including
  `os.environ`, before importing and serving the FastAPI application.

## [1.0.2] — 2026-08-31

### Fixed
- Publish the complete Workbench middleware contract, including trusted absolute-redirect
  handling required by `hedron-posit>=1.0.0`.
- Verify immutable PyPI artifacts against locally built wheels before a release can reuse an
  existing package version.

## [1.0.1] — 2026-08-24

### Fixed
- Accept full Workbench `rserver-url` values in `UVICORN_ROOT_PATH` and rediscover
  the mount when an inherited hint targets a different bound listener port.

### Changed
- Broaden direct Starlette compatibility to `>=0.40.0`.

## [0.43.0] — 2026-08-16

### Changed
- Coordinated train tip `0.43.0` (in-tree cut; tag/PyPI deferred).

## [0.42.0] — 2026-08-14

### Added
- Phase 0.42 production-grade Web Component platform graduation (D-070).

### Changed
- Coordinated train tip `0.42.0` (in-tree cut; tag/PyPI deferred).

## [1.0.0] — 2026-08-12

### Security

- Raise the Starlette floor to ``>=1.3.1`` so installs resolve patched releases
  for FormParser, URL authority, StaticFiles, and HTTPEndpoint advisories
  (PYSEC-2026-161 / 248 / 249 / 2280 / 2281).


### Added

- Initial release of `fastapi-workbench`: a framework-neutral Posit Workbench /
  RStudio Server deployment adapter extracted from `hedron-workbench`.
- Pre-import launcher (`run`, `check`, `doctor`), pure resolver, `workbenchify`
  wrap-once ASGI middleware, mount helpers, and redacted diagnostics (`FWB-0001`
  through `FWB-0009`).
- Starlette and Uvicorn runtime dependencies only; no Hedron imports.

### Fixed

- Absolute-URL decode rejects semicolon path-smuggling via shared traversal checks (#142).
- `run_target` discovery respects an explicit mount hint when the mount is already known (#144).

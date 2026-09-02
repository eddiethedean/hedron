# Changelog

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

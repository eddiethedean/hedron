# Changelog

## [0.42.0] - 2026-08-14

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

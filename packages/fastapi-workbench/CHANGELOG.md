# Changelog

## [1.0.0] — 2026-08-12

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

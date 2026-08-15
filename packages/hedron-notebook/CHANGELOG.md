# Changelog

## [0.42.0] - 2026-08-14

### Added
- Phase 0.42 production-grade Web Component platform graduation (D-070).

### Changed
- Coordinated train tip `0.42.0` (in-tree cut; tag/PyPI deferred).

## [0.1.0] — 2026-08-06

### Fixed

- Enforce the preview session token on HTTP and WebSocket requests (`hedron_preview_token`
  query parameter, `X-Hedron-Preview-Token` header, or the HttpOnly session cookie seeded
  after the first successful query/header auth). Missing or wrong tokens now fail closed
  with HTTP 401 / WebSocket close 4401 instead of serving the app to anyone who can reach
  the bound port (#161).


### Added

- Initial Alpha release of `NotebookPreview` / `start_preview` (RFC-0042):
  random port and session token, iframe and external-link modes, root-path
  prefix support, hosted/public host warnings, and injectable server for tests.
- Optional `hedron.plugins` FeatureManifest registration.

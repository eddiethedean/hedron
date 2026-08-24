# Changelog

## [0.2.1] — 2026-08-24

### Changed
- Updated the Hedron core and flagship compatibility floors for the 0.62 interaction train.

## [0.2.0] — 2026-08-20

### Changed

- Significant upgrade for phase 0.54 authoring-loop tooling (RFC-0081 / D-093).
- Independent Beta satellite tip `0.2.0`.

## [0.43.0] — 2026-08-16

### Changed
- Coordinated train tip `0.43.0` (in-tree cut; tag/PyPI deferred).

## [0.42.0] — 2026-08-14

### Added
- Phase 0.42 production-grade Web Component platform graduation (D-070).

### Changed
- Coordinated train tip `0.42.0` (in-tree cut; tag/PyPI deferred).

## [0.1.0] — 2026-08-06

### Added
- inspect_features consumes included bundles (localhost/offline).


### Fixed

- Enforce the preview session token on HTTP and WebSocket requests (`hedron_preview_token`
  query parameter, `X-Hedron-Preview-Token` header, or the HttpOnly session cookie seeded
  after the first successful query/header auth). Missing or wrong tokens now fail closed
  with HTTP 401 / WebSocket close 4401 instead of serving the app to anyone who can reach
  the bound port (#161).
- Preview waits for uvicorn listen before marking the server started (#278).
- Preview cookie ``Path`` is sanitized before ``Set-Cookie`` (#283).


### Added

- Initial Alpha release of `NotebookPreview` / `start_preview` (RFC-0042):
  random port and session token, iframe and external-link modes, root-path
  prefix support, hosted/public host warnings, and injectable server for tests.
- Optional `hedron.plugins` FeatureManifest registration.

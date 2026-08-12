## [Unreleased]

### Fixed

- Enforce the preview session token on HTTP and WebSocket requests (`hedron_preview_token`
  query parameter or `X-Hedron-Preview-Token` header). Missing or wrong tokens now fail
  closed with HTTP 401 / WebSocket close 4401 instead of serving the app to anyone who
  can reach the bound port (#161).

## [0.1.0] — 2026-08-06

### Added

- Initial Alpha release of `NotebookPreview` / `start_preview` (RFC-0042):
  random port and session token, iframe and external-link modes, root-path
  prefix support, hosted/public host warnings, and injectable server for tests.
- Optional `hedron.plugins` FeatureManifest registration.

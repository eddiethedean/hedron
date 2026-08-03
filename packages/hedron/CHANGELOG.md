# Changelog

All notable changes to `hedron` are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html)
with the Hedron coordinated release train (`0.N.0` for phase `0.N`).

## [0.2.0] - 2026-08-03

Initial FastAPI flagship distribution for the secure HTML/HTMX application MVP.

### Added

- Thin `Hedron(FastAPI)` facade with composable lifespan, security profiles, and
  bundled HTMX 2.0.10 static assets.
- `HedronRouter` / `HedronRoute` with `@page`, `@component`, `@action`, and
  `include_component` for reusable `@addressable` descriptors.
- Response helpers: `HTML`, `ComponentResponse`, `PageResponse`, `FragmentResponse`,
  `FileComponentResponse`, and `hedron_response`.
- HTMX page/fragment selection, approved headers, OOB/trigger helpers, and safe
  targets.
- CSRF integration for cookie-authenticated unsafe actions, safe redirects,
  private authenticated caching defaults, and security header profiles.
- `SessionState[T]` FastAPI session adapter.
- OpenAPI `text/html` responses, deterministic operation IDs, and `x-hedron-*`
  metadata.
- Interaction built-ins: `AutoForm`, `RefreshButton`, `Lazy`, `Pagination`,
  `Loading`, and retryable `ErrorState`.
- Minimal CLI: `hedron routes`, `hedron components`, `hedron preview`.
- Optional `hedron[dev]` Explorer preview via `hedron-explorer`.

[0.2.0]: https://github.com/eddiethedean/hedron/releases/tag/v0.2.0

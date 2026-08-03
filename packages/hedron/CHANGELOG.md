# Changelog

All notable changes to `hedron` are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html)
with the Hedron coordinated release train (`0.N.0` for phase `0.N`).

## [0.2.0] - 2026-08-03

Initial FastAPI flagship distribution for the secure HTML/HTMX application MVP.

### Added

- Thin `Hedron(FastAPI)` facade with composable lifespan, security profiles,
  `session_secret` warnings/strict gating, Explorer modes, and bundled HTMX
  2.0.10 via `/hedron-static/` (`mount_hedron_static` for plain FastAPI).
- `HedronRouter` / `HedronRoute` with `@page`, `@component`, `@action`, and
  `include_component` for reusable `@addressable` descriptors; plain `HTML(...)`
  conversion on `HedronRoute`.
- Response helpers: `HTML`, `ComponentResponse`, `PageResponse`, `FragmentResponse`,
  `FileComponentResponse`, and `hedron_response`.
- HTMX page/fragment selection, history-restore PAGE mode, approved headers,
  `oob_swap` / trigger helpers, and safe targets.
- CSRF integration that reuses the cookie across GETs and accepts header or
  `csrf_token` form field; safe redirects; private authenticated caching;
  security header profiles.
- `SessionState[T]` via `session_state(key, model)` FastAPI dependency factory.
- OpenAPI `text/html` responses, deterministic operation IDs, and `x-hedron-*`
  metadata.
- Interaction built-ins: `AutoForm`, `RefreshButton`, `Lazy`, `Poll`,
  `InfiniteScroll`, `Pagination`, `Loading`, and retryable `ErrorState`.
- Minimal CLI: `hedron [--app module:attr] routes|components|preview`.
- Optional `hedron[dev]` Explorer preview via `hedron-explorer`.

[0.2.0]: https://github.com/eddiethedean/hedron/commits/main

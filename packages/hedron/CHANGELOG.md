# Changelog

All notable changes to `hedron` are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html)
with the Hedron coordinated release train (`0.N.0` for phase `0.N`).

## [0.3.0] - 2026-08-03

Authoring, styles, assets, and themes for the FastAPI flagship.

### Added

- `[tool.hedron]` configuration loader and `Hedron(theme=..., build_dir=..., production=...)`.
- CLI commands: `build`, `dev`, `inspect`, and `eject` (plus existing routes/components/preview).
- Build orchestration that compiles HDN/CSS, fingerprints assets, and atomically
  promotes versioned manifests; production lifespan rejects missing manifests.
- Manifest-driven `/hedron-assets` StaticFiles mounting and page asset injection.
- Strict CSP without `style-src 'unsafe-inline'` for external stylesheets.
- First-party `hedron-disclose` Web Component with HTMX swap-safe lifecycle.

### Fixed / hardened

- Same-device atomic build promote (avoids cross-device rename failures) and CSS
  `url(...)` rewrite to fingerprinted `/hedron-assets/...` paths.
- Production loads compiled HDN from the build manifest; runtime compile is gated.
- `RenderResult.assets` filled from the active build manifest during response assembly.
- `hedron-disclose` uses `textContent` for labels, preserves light-DOM children, and
  rebinds when the swap target is the element itself.
- CLI hints when the registry is empty without `--app`; `eject` exits non-zero when
  nothing is written.
- `run_program` exported from the public `hedron` API; static mounts live in
  `hedron.static_mount` to avoid lifespan↔app circular imports.

[0.3.0]: https://github.com/eddiethedean/hedron/releases/tag/v0.3.0

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

[0.2.0]: https://github.com/eddiethedean/hedron/releases/tag/v0.2.0

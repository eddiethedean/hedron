# Changelog

All notable changes to `hedron` are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html)
with the Hedron coordinated release train (`0.N.0` for phase `0.N`).

## [0.6.0] - 2026-08-03

Visualization extras, typed HTMX interaction envelope, and first-party content/auth helpers.

### Added

- `HtmxRequest`, `InteractionResult`, `InteractionPolicy`, `FragmentRegion`, OOB helpers.
- Semantic HTMX status handlers (422 validation fragments; JSON for non-HTMX).
- Declared fragment regions on `@page`, `Vary` for page/fragment(/target), form `hx-sync` defaults.
- Extras: `charts`, `markdown`, `code`, `images`, `email`, `sanitize`, `auth`.
- `Markdown`, email/code/image helpers, Authlib conveniences, icon re-exports.
- `htmx_vary_dimensions` for cache/response variation documentation.

## [0.5.0] - 2026-08-03

Data application toolkit on the FastAPI flagship: caching decorators, upload/download
helpers, ColorMode persistence, and re-exports for `hedron-data` / Auto / utilities.

### Added

- `cache_data` / `cache_component` with scoped keys and single-flight.
- `FileUpload`, `DownloadButton`, `safe_download_response`, `validate_upload_size`.
- ColorMode cookie/session helpers.
- Optional extra `hedron[data]` → `hedron-data==0.5.0`.
- Lazy `DataTable` / `DataEditor` imports with install guidance when `hedron-data` is absent.
- Re-exports for DataTable, DataEditor, Auto, utilities, and ColorMode.

### Fixed

- Cache rejects `user` / `tenant` / `session` scopes without `vary_on`, and public-scope
  request/session positional args.
- Build fingerprints registered plugin CSS assets (DataEditor host stylesheet).
- HTMX 2 context exposes every official request header, including history restores without
  `HX-Request`; response helpers cover replace/reselect and all trigger timings.
- Full pages apply CSP-compatible HTMX defaults for history, eval/scripts, same-origin requests,
  indicator styles, and native form-validity reporting.

## [0.4.0] - 2026-08-03

Developer platform for the FastAPI flagship.

### Added

- CLI `new`, `check` (text/JSON/SARIF), `graph`, and `audit-components`.
- Plugin loader with entry points, compatibility gates, lifespan hooks, and rollback.
- Public `hedron.testing` helpers and optional `hedron[browser]` hooks.
- Inference explanations/overrides in CLI `preview`.

### Fixed

- Plugin loads roll back the full registry builder (not only Explorer panels) on failure.
- Plugin `start()` failures roll back registry contributions and Explorer panels.
- `plugins = []` loads no plugins; unset plugins discover all at lifespan and build; missing enabled names error.
- Version compatibility uses `packaging` specifier sets (fail closed on invalid ranges).
- Lifespan always surfaces plugin load/`start` failures and shuts down started hooks.
- CSRF applies when any declared method is unsafe for page/component/action routes, including `include_component`.
- CSRF cookies set `Secure` when the request is HTTPS (all profiles).
- Local redirects and HTMX local-path headers reject backslash open-redirect forms; `redirect_external` fails closed without a policy.
- Production forces Explorer `development` mode off; scaffolds default `explorer = "off"`.
- Lifespan applies `[tool.hedron] component_roots` to `app.state.hedron_component_roots`.
- CLI `check`/`graph`/`audit-components` apply discovery; evergreen INFORMATION findings do not fail the exit gate; `new` guards existing `app.py`/`pyproject.toml`.
- Builds match lifespan plugin discovery and restore the registry afterward so in-process app startup can reload plugins; `override_dependencies` restores FastAPI overrides.
- Asset `href` values are HTML-escaped before page injection.

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
- Production loads compiled HDN from the build manifest; runtime compile is gated
  on the compile APIs with build force-allow.
- `RenderResult.assets` filled from the active build manifest; injection deduped.
- First-load CSRF form/`hx-headers` tokens match the CSRF cookie
  (`csrf_token_for_request`).
- Unique HDN/css-symbol artifact paths from logical ids; style component ids honor
  `STYLE_COMPONENT_ID` when present.
- `hedron-disclose` uses `textContent` for labels, preserves light-DOM children, and
  rebuilds incomplete chrome cleanly.
- CLI hints when the registry is empty without `--app`; `eject` exits non-zero when
  nothing is written.
- `run_program` exported from the public `hedron` API; static mounts live in
  `hedron.static_mount` to avoid lifespan↔app circular imports.
- Explorer mounting follows `SecurityPolicy.explorer_enabled` unless `explorer=` is set.

[0.4.0]: https://github.com/eddiethedean/hedron/releases/tag/v0.4.0
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

[0.5.0]: https://github.com/eddiethedean/hedron/releases/tag/v0.5.0

[0.6.0]: https://github.com/eddiethedean/hedron/releases/tag/v0.6.0

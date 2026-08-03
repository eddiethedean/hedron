# Changelog

All notable changes to `hedron-explorer` are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html)
with the Hedron coordinated release train (`0.N.0` for phase `0.N`).

## [0.5.0] - 2026-08-03

Explorer panels for cache traces, data policy, and Auto renderer evidence.

### Added

- First-party `/hedron-explorer/cache`, `/data`, and `/auto` panels.
- `/data` lists registered DataTable/DataEditor components and a sample writable policy.

## [0.4.0] - 2026-08-03

Full HTMX Explorer shell with panels for components, routes, graph, security,
accessibility, packages, and settings; sanitized JSON APIs; rate limiting and
audit hooks; mutation simulation disabled by default.

### Fixed

- HDN/CSS reads are allowlisted under configured project component roots only (registry `folder_path` is not a trusted root).
- Preview markup is embedded in a sandboxed iframe (`srcdoc`); absolute paths stay basename-redacted.
- Static CSS is served via a routed `FileResponse` under Explorer guards (not a bare StaticFiles mount).
- `/api/simulate` rejects bad JSON and unknown keys; CSRF is required when the CSRF cookie is present.
- Unknown components return HTTP 404.

[0.4.0]: https://github.com/eddiethedean/hedron/releases/tag/v0.4.0
[0.3.0]: https://github.com/eddiethedean/hedron/releases/tag/v0.3.0

## [0.3.0] - 2026-08-03

Coordinated release train bump with `hedron` 0.3.0. Explorer preview unchanged;
full style/HDN panels remain phase 0.4.

## [0.2.0] - 2026-08-03

Initial Explorer preview for the FastAPI MVP.

### Added

- Development-only router for routes, components, previews, HTMX inference, and
  security findings.
- Production absence by default with redacted metadata views.
- Shared registry identity with `hedron` routing and OpenAPI.

[0.2.0]: https://github.com/eddiethedean/hedron/releases/tag/v0.2.0

[0.5.0]: https://github.com/eddiethedean/hedron/releases/tag/v0.5.0

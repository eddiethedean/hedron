## [0.15.0] — 2026-08-05

### Added

- Coordinated Beta train with phase 0.15 data-app surface completeness.

## [0.14.0] — 2026-08-05

### Added

- Phase 0.14 portable runtimes and acceleration (conformance kit hooks, optional native
  acceleration, HDJ instrumentation where applicable).

## [0.13.0] — 2026-08-05

### Added

- Phase 0.13 advanced async and observability.

# Changelog

## [0.12.0] — 2026-08-05

### Added

- Phase 0.12 data and visualization scale contracts and adapters.



## [0.11.0] — 2026-08-04

### Added
- Phase 0.11 native framework depth (Flask Blueprint/`init_app`, Django AppConfig/forms/QuerySet,
  portable adapter harness, HDJ manifests/CSP inventory, Celery/RQ bridges, live helpers).

### Fixed
- `/inventory` loads project `.hdj` template reports when available (not an empty stub).


## [0.10.1] - 2026-08-04

### Changed
- Coordinated patch train with the 0.10.1 security and correctness fixes.

## [0.10.0] - 2026-08-04

- Joined the coordinated 0.10 live-interaction package train.

## [0.9.0] - 2026-08-04

- Removed HDN source, graph, and API panels.

## [0.8.0] - 2026-08-03

### Added

- Public stability catalog, deprecation/semver policy, upgrade guide, and threat model.
- Performance budgets with enforcement tests; three-engine browser HTMX matrix scaffolding.
- SBOM, license inventory, browser-asset audit, and release evidence bundle scripts.
- Flask/Django hardening suites and Django Supported floor `>=5.2,<6`.

### Changed

- Feature freeze: no new subsystems, adapters, or transports on the 0.8 train.

## [0.7.0] — 2026-08-03

- Phase 0.7 portable adapters, operations, and jobs train.


All notable changes to `hedron-explorer` are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html)
with the Hedron coordinated release train (`0.N.0` for phase `0.N`).

## [0.6.0] - 2026-08-03

Explorer visualization panel and richer HTMX interaction simulation.

### Added

- `/hedron-explorer/charts` visualization panel (backend, assets, a11y/security notes).
- `/api/simulate` modes: fragment/boosted/history/validation with region allowlist checks,
  cache variation, and inference traces.

## [0.5.0] - 2026-08-03

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

[0.6.0]: https://github.com/eddiethedean/hedron/releases/tag/v0.6.0

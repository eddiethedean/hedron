# Changelog

## [0.25.2] — 2026-08-10

### Fixed

- Simulate CSRF fallback uses strategy cookie/header names from `resolve_csrf_strategy()`.
- `/api/simulate` always requires CSRF validation (ignores `csrf_enabled=False`).

### Changed

- Coordinated Beta patch with `hedron` 0.25.2.

## [0.25.1] — 2026-08-09

### Changed

- Coordinated Beta patch release with `hedron` 0.25.1.

## [0.25.0] — 2026-08-09

### Changed

- Coordinated Beta train bump with `hedron` 0.25.0.

## [0.24.0] — 2026-08-09

### Changed

- Coordinated Beta train bump with `hedron` 0.24.0.
- Live-transport disposition `polling_only` (D-053): polling Supported; live helpers remain experimental.

## [0.23.0] — 2026-08-08

### Changed

- Promotes locked CRUD/admin facade to API `stable`.

## [0.22.0] — 2026-08-08

### Added

- Phase 0.22 CSRF / SecurityPolicy composition (`CSRF-022`, `HEADERS-022`, `FORM-022`).

## [0.21.0] — 2026-08-08

### Changed

- Coordinated Beta train with phase 0.21 human AT engineering (see `hedron-core` /
  `hedron` changelogs). Sessions (SR/PARTICIPANT) remain Planned / not Supported.

## [0.20.0] — 2026-08-07

- Production security floor and adapter parity (phase 0.20 / D-051).


## [0.19.0] — 2026-08-07

### Added

- Phase 0.19 accessibility engineering and inclusive authoring (RFCs 0023 / 0051–0055, D-050):
  - `AccessibilityContract` catalog, standards profile, waiver/statement governance
  - Landmark safe attrs / real types, allowlisted `Page` scripts, PE form paths
  - Explorer accessibility review workspace, ATAG inspect/eject metadata
  - `AccessibilityScenario`, tree snapshots, axe/SARIF helpers; automated AT matrix


## [0.18.0] — 2026-08-06

### Changed

- Coordinated Beta train with phase 0.18 model demos / inference workflows.


## [0.17.0] — 2026-08-06

### Added

- Phase 0.17 reactive dashboards and agent interfaces (see ROADMAP §0.17 / RFCs 0040–0044).

## [0.16.0] — 2026-08-06

### Added

- Coordinated Beta train with phase 0.16 curated extras (`hedron-extras` optional).

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

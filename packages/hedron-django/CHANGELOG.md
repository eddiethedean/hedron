# Changelog

## [0.24.0] — 2026-08-09

### Changed

- Coordinated Beta train bump with `hedron` 0.24.0.
- Live-transport disposition `polling_only` (D-053): polling Supported; live helpers remain experimental.
- `sse_response` / `stream_text` moved off the package root to `hedron_django.experimental`
  (Flask parity). Prefer `poll_status_response` in production.

## [0.23.0] — 2026-08-08

### Changed

- Promotes locked CRUD/admin facade to API `stable`.
- Missing `CsrfViewMiddleware` is a deploy `Error` (`hedron.E003`).

### Security

- Fail-closed `validate_csrf()` on unsafe methods in `hedron_view` /
  `HedronDjango.respond` (bridges portable `csrf_token` → `csrfmiddlewaretoken`).
- `extra_headers` and evil `InteractionResult` headers fail closed via
  `validated_extra_headers` (HTTP 403).
- Fragment region string normalization uses a single `#` strip (`removeprefix`).

## [0.22.0] — 2026-08-08

### Added

- Phase 0.22 CSRF / SecurityPolicy composition (`CSRF-022`, `HEADERS-022`, `FORM-022`).

## [0.21.0] — 2026-08-08

### Fixed

- `respond(..., allow_undeclared_targets=...)` plumbed to component responses.

## [0.20.0] — 2026-08-07

- Production security floor and adapter parity (phase 0.20 / D-051).


## [0.19.0] — 2026-08-07

### Changed

- Coordinated Beta train with phase 0.19 accessibility engineering (see `hedron-core` /
  `hedron` / `hedron-explorer` changelogs for capability detail).


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
- Forms bridge maps radio/number/file widgets; `register_checks` is idempotent;
  `poll_status_response` exported from `live`.


## [0.10.1] - 2026-08-04

### Fixed
- Set `Cache-Control: private, no-store` on authenticated component/interaction responses.

## [0.10.0] - 2026-08-04

- Joined the coordinated 0.10 package train; FastAPI remains the Supported live host (D-044).

## [0.9.0] - 2026-08-04

- Joined the coordinated 0.9 package train; native framework depth remains planned for 0.11.

## [0.8.0] - 2026-08-03

### Added

- Public stability catalog, deprecation/semver policy, upgrade guide, and threat model.
- Performance budgets with enforcement tests; three-engine browser HTMX matrix scaffolding.
- SBOM, license inventory, browser-asset audit, and release evidence bundle scripts.
- Flask/Django hardening suites and Django Supported floor `>=5.2,<6`.

### Changed

- Feature freeze: no new subsystems, adapters, or transports on the 0.8 train.

## [0.7.0] - 2026-08-03

- Initial `hedron-django` package: `HedronDjango`, component/interaction responses,
  Django `reverse` support, CSRF/session thin helpers, and explicit QuerySet DataSource deferral (D-036).

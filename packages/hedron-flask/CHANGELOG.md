## [0.37.0]

- Coordinated train cut for phase 0.37 (D-065).

## [0.36.0] — 2026-08-13

- Coordinated Beta train cut for Web Component ABI foundation (D-064 / RFC-0060).

## [0.35.0] — 2026-08-13

### Added

- Coordinated Beta train cut for whole-fleet production-grade closure (D-063 / RFC-0068).

## [0.34.0] — 2026-08-13

### Added

- Coordinated Beta train cut for production-grade Gradio client interop (D-062 / RFC-0067).

# Changelog

## [0.33.0] — 2026-08-13

- Coordinated train bump for phase 0.33 (`hedron-posit` unified Posit adapter; D-061 / RFC-0066).

## [0.32.0] — 2026-08-12

- Coordinated train bump for phase 0.32 MCP production-grade graduation.


## [0.31.0] — 2026-08-12

- Coordinated `0.31.0` train: tooling-grade conformance/sim/notebook/sample-kit/Node+Java evaluators and `hedron migrate streamlit` (D-059 / RFC-0064 / RFC-0061).

## [0.30.0] — 2026-08-12

- Coordinated `0.30.0` train; `hedron-workbench` depends on `fastapi-workbench` 1.0.0 (phase 0.30 / D-058).


## [0.29.0] — 2026-08-11

### Changed

- Coordinated 0.29 train bump. Flask adapter does not import hedron-workbench.


## [0.28.2] — 2026-08-11

### Fixed

- Honor ``SecurityPolicy.allow_htmx_eval`` during render; PAGE-mode
  ``interaction_response`` injects page assets; CSRF Secure flag uses the shared
  ``hedron_core.csrf_secure`` helper (``FLASK_ENV`` / ``ENV`` parity retained).

### Changed

- Coordinated Beta patch to `0.28.2` (pin `>=0.28.2,<0.29`).

## [0.28.1] — 2026-08-10

### Fixed

- Pass mount-aware `static_href` (via `SCRIPT_NAME`) into page/HTMX asset injection.

### Changed

- Coordinated Beta patch to `0.28.1` (pin `>=0.28.1,<0.29`).

## [0.28.0] — 2026-08-10

### Added

- Production-grade graduation for `hedron-charts` / `hedron-native` Supported
  inventories (D-056 / RFC-0059): static/Matplotlib beginner charts, optional
  native escape acceleration with `HEDRON_NATIVE_DISABLE` fallback, interactive
  Auto quarantine, and SUPPLY-028 pin/SBOM evidence.

### Changed

- Coordinated Beta train bump to `0.28.0` (pin `>=0.28.0,<0.29`).
- Charts / sample-kit floors raised to `>=0.1.8,<0.2`; native to `>=0.1.1,<0.2`.


## [0.27.0] — 2026-08-10

### Added

- Production-grade graduation for the declared Supported satellite inventory
  (D-055 / RFC-0058): inventory freeze, `v0.26.0` upgrade fixtures, host-only
  adapter/data/HDJ/extras evidence, portable parity, and REVIEW-027 disposition.

### Changed

- Mount `/hedron-static` and inject shared PAGE HTMX assets the same way as the
  FastAPI flagship (`mount_hedron_static` / core `page_assets`).
- Coordinated Beta train bump to `0.27.0` (pin `>=0.27.0,<0.28`).

## [0.26.1] — 2026-08-10

### Changed

- Coordinated Beta patch release.

## [0.26.0] — 2026-08-10

### Added

- Production-grade graduation packet for the declared Supported CRUD/admin inventory
  (D-054 / RFC-0057): machine-readable inventory, `v0.25.2` upgrade fixtures, secured
  Explorer evidence, FastAPI ops smoke, and REVIEW-026 security disposition.

### Changed

- Coordinated Beta train bump to `0.26.0` (pin `>=0.26.0,<0.27`).

## [0.25.2] — 2026-08-10

### Fixed

- Sync CSRF cookie names between HedronFlask extension and SecurityPolicy/strategy.
- `hedron_route` resolves and honors the app SecurityPolicy (including csrf_enabled=False).
- Propagate `allow_undeclared_targets` for InteractionResult responses.
- Use shared `cookie_path_for_mount` for CSRF cookie Path under SCRIPT_NAME mounts.
- `_maybe_prepare` fails closed under a running loop; add `respond_async` and `skip_prepare`.
- Experimental SSE accepts only `SseEvent` (no raw string framing).

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
- `hedron_flask.live.__all__` exports polling only; SSE/stream warn and belong in
  `hedron_flask.experimental`.
- `respond(..., allow_undeclared_targets=True)` applies to `InteractionResult` paths.
- Fragment responses default toward `Cache-Control: private, no-store` and align `Vary`.

### Security

- `security="strict"` forces Secure CSRF cookies (FastAPI STRICT parity) without requiring
  `csrf_cookie_secure=True`.
- CSRF `Secure` honors `X-Forwarded-Proto: https` only from `HEDRON_TRUSTED_PROXIES` /
  Flask `HEDRON_TRUSTED_PROXIES` config / extension `trusted_peers`.
- CSRF `Secure` also forces under `HEDRON_ENV=production` / `prod`.
- `InteractionResult` with `status_code=204` and OOB updates returns HTTP 403 (FastAPI parity).
- History-restore HTMX requests may omit `HX-Target` when fragment regions are declared.

## [0.23.0] — 2026-08-08

### Changed

- Promotes locked CRUD/admin facade to API `stable`.

### Security

- `extra_headers` and evil `InteractionResult` headers fail closed via
  `validated_extra_headers` (HTTP 403).
- Fragment region string normalization uses a single `#` strip (`removeprefix`).

## [0.22.0] — 2026-08-08

### Added

- Phase 0.22 CSRF / SecurityPolicy composition (`CSRF-022`, `HEADERS-022`, `FORM-022`).

## [0.21.0] — 2026-08-08

### Fixed

- `@action` / `include_component` honor `fragment_regions` and `allow_undeclared_targets`.
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
- `include_component` derives CSRF from methods (no longer hard-coded off on unsafe methods).
- Public `wrap_hedron_view` export for factory apps.


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

- Initial `hedron-flask` package: `HedronFlask`, component/interaction responses,
  Flask `url_for` reversal, CSRF double-submit helpers, and `AuthSignal` session mapping.

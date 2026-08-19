# Changelog

## [0.50.1] — 2026-08-18

### Changed
- Coordinated train tip `0.50.1`.

### Fixed
- `/api/dashboard-graph` serializes `app.state.hedron_dashboard_graph` when set.
- Packages panel renders Hedron nodes returned by `ExplorerProvider.render`.
- Maps page shows compiled MapPlan facts (origins, attribution, CSP).
- Security page lists the live audit tail.
- `hedron-explorer[fastapi]` extra matches the base FastAPI upper bound.

## [0.50.0] — 2026-08-18

### Changed
- Coordinated train tip `0.50.0` (in-tree cut; tag/PyPI deferred).

### Added
- Explorer architecture services/views split, ExplorerProvider v1, query pagination,
  diffs, headless CLI parity, bounded lab, and HTMX authoring primitives (#496–#500, #502, #503).

### Fixed
- Query/CLI surfaces no longer silent-slice; truncation emits ``HED-EXPLORER-0001``.
- Graph JSON includes ``browser_module`` edges; ``find_component`` matches exact ``logical_id``.
- ``element-simulate`` requires CSRF; junk simulate ``status`` is 400; falsey CSRF validators 403.
- Diff snapshots a real catalog baseline; ``/packages`` runs providers in isolation.

## [0.49.1] — 2026-08-18

### Changed
- Coordinated train tip `0.49.1` (in-tree patch; tag/PyPI deferred).

### Fixed
- HDJ inventory refuses symlink targets that resolve outside the allowlisted root (#275).

## [0.49.0] — 2026-08-17

### Added
- Phase 0.49 FastAPI/Pydantic convergence (D-081 / D-084 / RFC-0076).

### Changed
- Coordinated train tip `0.49.0` (in-tree cut; tag/PyPI deferred).


## [0.48.0] — 2026-08-17

### Added
- Phase 0.48 first-class HTMX extension integration (D-080 / D-083 / RFC-0075).

### Changed
- Coordinated train tip `0.48.0` (in-tree cut; tag/PyPI deferred).

## [0.47.0] — 2026-08-17

### Added
- Phase 0.47 first-class maps (`hedron-maps` 0.1.0) on the coordinated train (D-078 / D-082 / RFC-0074).

### Changed
- Coordinated train tip `0.47.0` (in-tree cut; tag/PyPI deferred).

## [0.46.0] — 2026-08-16

### Added
- Explorer Features panel consumes included FeatureBundles.

### Changed
- Coordinated train tip `0.46.0`.


## [0.45.0] — 2026-08-16

### Added
- Phase 0.45 Explorer catalog/projection/drift/provenance panels consume public catalog APIs.

### Changed
- Coordinated train tip `0.45.0` (in-tree cut; tag/PyPI deferred).

## [0.44.0] — 2026-08-16

### Added
- Phase 0.44 type-driven authoring (D-072 / D-076 / RFC-0071).

### Changed
- Coordinated train tip `0.44.0` (in-tree cut; tag/PyPI deferred).


## [0.43.0] — 2026-08-16

### Added
- Phase 0.43 refreshable views, command handles, and typed updates (D-071 / RFC-0070).

### Changed
- Coordinated train tip `0.43.0` (in-tree cut; tag/PyPI deferred).

## [0.42.0] — 2026-08-14

### Added
- Phase 0.42 production-grade Web Component platform graduation (D-070).

### Changed
- Coordinated train tip `0.42.0` (in-tree cut; tag/PyPI deferred).

## [0.41.0] — 2026-08-15

- Phase 0.41 browser composition, bounded draft transfer, navigation, tracing, failure isolation, and regression closure (D-069).

## [0.40.0] — 2026-08-14

### Added
- Phase 0.40 authoring kit, metadata parity, React migration matrix, and remediation packet (D-068).

## [0.39.0] — 2026-08-14

### Added
- Phase 0.39 rich data ABI, OptimisticMutation, chartlink, and remediation packet (D-067).

## [0.38.0] — 2026-08-14

- Phase 0.38 high-fidelity charts / train alignment (D-066 / RFC-0069).


## [0.37.0] — 2026-08-14

- Coordinated train cut for phase 0.37 (D-065).

## [0.36.0] — 2026-08-13

- Coordinated Beta train cut for Web Component ABI foundation (D-064 / RFC-0060).

## [0.35.0] — 2026-08-13

### Added

- Coordinated Beta train cut for whole-fleet production-grade closure (D-063 / RFC-0068).

## [0.34.0] — 2026-08-13

### Added

- Coordinated Beta train cut for production-grade Gradio client interop (D-062 / RFC-0067).

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

- Coordinated 0.29 train bump.


## [0.28.2] — 2026-08-11

### Changed

- Coordinated Beta patch to `0.28.2` (pin `>=0.28.2,<0.29`).

## [0.28.1] — 2026-08-10

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

- Coordinated Beta train bump to `0.27.0` (pin `>=0.27.0,<0.28`).

## [0.26.1] — 2026-08-10

### Fixed

- Generate Explorer navigation, component detail, and static-asset links relative to a configured Hedron mount path.

## [0.26.0] — 2026-08-10

### Added

- Production-grade graduation packet for the declared Supported CRUD/admin inventory
  (D-054 / RFC-0057): machine-readable inventory, `v0.25.2` upgrade fixtures, secured
  Explorer evidence, FastAPI ops smoke, and REVIEW-026 security disposition.

### Changed

- Coordinated Beta train bump to `0.26.0` (pin `>=0.26.0,<0.27`).

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

## [0.12.0] — 2026-08-05

### Added

- Phase 0.12 data and visualization scale contracts and adapters.



## [0.11.0] — 2026-08-04

### Added
- Phase 0.11 native framework depth (Flask Blueprint/`init_app`, Django AppConfig/forms/QuerySet,
  portable adapter harness, HDJ manifests/CSP inventory, Celery/RQ bridges, live helpers).

### Fixed
- `/inventory` loads project `.hdj` template reports when available (not an empty stub).


## [0.10.1] — 2026-08-04

### Changed
- Coordinated patch train with the 0.10.1 security and correctness fixes.

## [0.10.0] — 2026-08-04

- Joined the coordinated 0.10 live-interaction package train.

## [0.9.0] — 2026-08-04

- Removed HDN source, graph, and API panels.

## [0.8.0] — 2026-08-03

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

## [0.6.0] — 2026-08-03

Explorer visualization panel and richer HTMX interaction simulation.

### Added

- `/hedron-explorer/charts` visualization panel (backend, assets, a11y/security notes).
- `/api/simulate` modes: fragment/boosted/history/validation with region allowlist checks,
  cache variation, and inference traces.

## [0.5.0] — 2026-08-03

### Added

- First-party `/hedron-explorer/cache`, `/data`, and `/auto` panels.
- `/data` lists registered DataTable/DataEditor components and a sample writable policy.

## [0.4.0] — 2026-08-03

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

## [0.3.0] — 2026-08-03

Coordinated release train bump with `hedron` 0.3.0. Explorer preview unchanged;
full style/HDN panels remain phase 0.4.

## [0.2.0] — 2026-08-03

Initial Explorer preview for the FastAPI MVP.

### Added

- Development-only router for routes, components, previews, HTMX inference, and
  security findings.
- Production absence by default with redacted metadata views.
- Shared registry identity with `hedron` routing and OpenAPI.

[0.2.0]: https://github.com/eddiethedean/hedron/releases/tag/v0.2.0

[0.5.0]: https://github.com/eddiethedean/hedron/releases/tag/v0.5.0

[0.6.0]: https://github.com/eddiethedean/hedron/releases/tag/v0.6.0

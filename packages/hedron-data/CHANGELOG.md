# Changelog

## [0.28.2] — 2026-08-11

### Fixed

- Serialize ``InMemoryDataSource.apply`` / ``fetch`` with an instance lock so
  concurrent nonconflicting commits cannot silently lose updates (#114).

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

- Escape SQLAlchemy `LIKE` / `ilike` metacharacters (`%`, `_`, `\`) in allowlisted search.

### Changed

- Coordinated Beta patch with `hedron` 0.25.2 (docs honesty + package train alignment).

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
- Column write policy is deny-by-default: `writable` must be explicitly `True`
  (DataEditor writable set + AG Grid `editable`).

## [0.22.0] — 2026-08-08

### Added

- Phase 0.22 CSRF / SecurityPolicy composition (`CSRF-022`, `HEADERS-022`, `FORM-022`).

## [0.21.0] — 2026-08-08

### Fixed

- DataEditor Escape cancels edit without queuing/saving; 403 responses skip `res.json()`.

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
- `DjangoQuerySetDataSource` deny-by-default allowlists when sort/filter lists are omitted.


## [0.10.1] - 2026-08-04

### Fixed
- Fail closed on unsupported SQLAlchemy `DataQuery.projection`.

## [0.10.0] - 2026-08-04

- Joined the coordinated 0.10 package train.

## [0.9.0] - 2026-08-04

- Joined the coordinated 0.9 package train and updated plugin compatibility metadata.

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


## [0.6.0] - 2026-08-03

- Async `VisualizationSource` protocol and viz row/payload defaults.
- `SQLAlchemyDataSource` adapter (`hedron-data[sqlalchemy]` / `[sqlmodel]`).
- AG Grid Community host shim and `ensure_aggrid_assets()` (`hedron-data[aggrid]`).
- Bounded SQLAlchemy paging: `OFFSET`/`LIMIT` applied in SQL (not collect-all-then-slice).

## [0.5.0] - 2026-08-03

- Initial `hedron-data` package: data-source protocols, `DataTable`, `DataEditor`,
  in-memory paged sources (sync + async), optional Narwhals dataframe normalization, and
  Tabulator-shaped browser adapter assets.
- Async sources require explicit `page=` at construction; sync `apply_changes` raises for
  awaitable `apply` and `apply_changes_async` awaits correctly.
- Writable-field policy rejects forged read-only/hidden fields, unauthorized deletes, and
  non-mapping inserts.
- DataEditor host: undo DOM restore, insert/delete, save modes, conflict actions, choices
  and boolean editors, escaped selectors; CSS fingerprinted via plugin assets.

[0.5.0]: https://github.com/eddiethedean/hedron/releases/tag/v0.5.0

[0.6.0]: https://github.com/eddiethedean/hedron/releases/tag/v0.6.0

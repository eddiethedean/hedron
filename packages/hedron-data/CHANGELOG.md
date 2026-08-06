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

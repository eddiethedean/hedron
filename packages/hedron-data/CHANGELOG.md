# Changelog

## [0.60.2] — 2026-08-24

### Fixed
- Coordinated Workbench and Connect integration fixes from the 0.60.2 maintenance release.

### Changed
- Coordinated train tip `0.60.2` (in-tree patch; tag/PyPI published).

## [0.60.1] — 2026-08-23

### Fixed
- Repaired data-source, transform, tree, pivot, import, spreadsheet, and collaboration
  integrity edge cases.

### Changed
- Coordinated train tip `0.60.1` (in-tree patch; tag/PyPI deferred).

## [0.60.0] — 2026-08-23

### Added
- Custom theme platform, typed modern colors, deterministic ThemeSpec packages, accessibility modes, scoped recipes, preference selection, and zero-application-CSS component evidence (RFC-0089 / D-108).

### Changed
- Coordinated train release 0.60.0 (tag and PyPI publication tracked separately).


## [0.59.0] — 2026-08-22

### Added
- Phase 0.59 modern CSS platform, typed controls, responsive containers, shell/workflow primitives, and release evidence (RFC-0087 / D-106 / D-107).

### Changed
- Coordinated train release `0.59.0` (published on PyPI).


## [0.58.1] — 2026-08-22

### Changed
- Coordinated train tip `0.58.1` (in-tree patch; tag/PyPI deferred).

## [0.58.0] — 2026-08-21

### Added
- Phase 0.58 progressive feature and styling authoring (RFC-0085 / D-101 / D-102 / D-105).

### Changed
- Coordinated train tip `0.58.0`, published on PyPI.

## [0.57.0] — 2026-08-21

### Added
- Phase 0.57 unified presentation / zero-application-CSS (RFC-0084 / D-099 / D-100).

### Changed
- Coordinated train tip `0.57.0` (in-tree cut; tag/PyPI deferred). Restores the 0.57
  train entry so package history matches docs/guides/release-notes.md (previously
  omitted between 0.58.0 and 0.56.1).

## [0.56.1] — 2026-08-21

### Changed
- Coordinated train tip `0.56.1` (in-tree patch; tag/PyPI deferred).

### Fixed
- Workspace Python quality upgrade: typing debt burn-down, safer best-effort exception logging, ASYNC/PTH/DTZ/RET ruff rules, and maintainability refactors without public API breaks.


## [0.56.0] — 2026-08-20

### Added

- Security control plane composition under `hedron_core.security_plane` (context, sensitivity, sinks, egress, budgets, intents, posture).

## [0.55.0] — 2026-08-20

### Changed
- Coordinated train tip `0.55.0` (in-tree cut; tag/PyPI deferred).

### Added
- Secure upgradeable workflow primitives (master-detail, capabilities, replay,
  uploads, CSP reporting, offline upgrade-report) under RFC-0082 / D-095 / D-096.

## [0.54.0] — 2026-08-20

### Changed

- Coordinated train tip `0.54.0` (published on GitHub and PyPI).
- Phase 0.54 authoring loop + application chrome (RFC-0081 / D-093 / D-094).

### Fixed

- Saved views reject malformed columns, selections, filters, and sort entries instead of
  coercing invalid persisted data.

## [0.53.0] — 2026-08-20

### Added

- Coordinated train tip `0.53.0` (in-tree Published; tag/PyPI deferred).
- Application DX contracts (RFC-0080 / D-091 / D-092): assets, diagnostics, routes,
  workflows, testgen, theming, discovery, and fleet doctor.

## [0.52.0] — 2026-08-20

### Changed
- Coordinated train tip `0.52.0` (in-tree Published; tag/PyPI deferred).
- Phase 0.52 conformance authority + Posit lifecycle (RFC-0079 / D-089 / D-090; #522).

## [0.51.2] — 2026-08-20

### Changed
- Coordinated train tip `0.51.2`.

### Fixed
- See flagship `hedron` changelog for the full 0.51.2 quality/typing list.

## [0.51.1] — 2026-08-20

### Changed
- Coordinated train tip `0.51.1` (in-tree patch; tag/PyPI deferred).

### Fixed
- See flagship `hedron` changelog for the full 0.51.1 bugfix list.

## [0.51.0] — 2026-08-19

### Changed
- Coordinated train tip `0.51.0` (in-tree; tag/PyPI deferred).

## [0.50.3] — 2026-08-19

### Changed
- Coordinated train tip `0.50.3`.

### Fixed
- HTMX `@command` and compiled refresh/patch responses stay fail-closed for undeclared targets.
- Tabular normalize, secret columns, draft-transfer names, and secret-like redaction no longer leak or false-match.
- Data/chart/patch/CSS/image/collab correctness (see tests/unit/test_bugfix_0503.py).

## [0.50.2] — 2026-08-19

### Changed
- Coordinated train tip `0.50.2` (in-tree patch; tag/PyPI deferred).

## [0.50.1] — 2026-08-18

### Changed
- Coordinated train tip `0.50.1`.

### Fixed
- Spreadsheet formula filter strips combining-mark prefixes before the dangerous-prefix check.
- `evaluate_formula` rejects bool, `None`, and unparseable cells instead of coercing them to `0.0`.

## [0.50.0] — 2026-08-18

### Changed
- Coordinated train tip `0.50.0` (in-tree cut; tag/PyPI deferred).

### Added
- Explorer architecture services/views split, ExplorerProvider v1, query pagination,
  diffs, headless CLI parity, bounded lab, and HTMX authoring primitives (#496–#500, #502, #503).

## [0.49.1] — 2026-08-18

### Changed
- Coordinated train tip `0.49.1` (in-tree patch; tag/PyPI deferred).

### Fixed
- Formula policy NFKC-folds lookalike prefixes and treats ``|`` as a DDE/CSV injection prefix (#263, #274).
- ODS ``row_repeat`` × column expansion is capped (#292).
- ``DataWorkspace`` honors ``columns`` and ``form_overrides`` (#340).

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

### Fixed
- Generated DataWorkspace list views bind ``offset`` / ``limit`` / ``sort`` / ``q``
  and allowlisted field filters into ``DataQuery`` (#354).
- DataWorkspacePolicy hooks receive request identity and deny closed on
  signature mismatch instead of HTTP 500 (#355).

## [0.46.0] — 2026-08-16

### Added
- DataWorkspace / DataWorkspacePolicy compiling to FeatureBundle over DataEditorSource.

### Changed
- Coordinated train tip `0.46.0`.


## [0.45.0] — 2026-08-16

### Added
- Phase 0.45 current-surface PackageProjection; direct APIs remain usable without a catalog.

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

### Security

- Spreadsheet formula reject/sanitize policies strip leading whitespace, ASCII
  controls, and BOM, and treat fullwidth ``＝＋－＠`` prefixes as dangerous so
  padded formula-injection payloads cannot bypass the check (#169). Tabulator
  ``sanitizeFormulaCell`` stays in lockstep.

## [0.31.0] — 2026-08-12

- Coordinated `0.31.0` train: tooling-grade conformance/sim/notebook/sample-kit/Node+Java evaluators and `hedron migrate streamlit` (D-059 / RFC-0064 / RFC-0061).

## [0.30.0] — 2026-08-12

- Coordinated `0.30.0` train; `hedron-workbench` depends on `fastapi-workbench` 1.0.0 (phase 0.30 / D-058).


## [0.29.0] — 2026-08-11

### Changed

- Coordinated 0.29 train bump.


## [0.28.2] — 2026-08-11

### Fixed

- Serialize ``InMemoryDataSource.apply`` / ``fetch`` with an instance lock so
  concurrent nonconflicting commits cannot silently lose updates (#114).
- DataEditor CSV export keeps pending edits, uses RFC quoting (not
  ``JSON.stringify``), and sanitizes spreadsheet formula prefixes like
  ``DataTable.to_csv`` (#112).
- DataEditor save success clears only the submitted batch (by operation id),
  so edits made while a request is in flight remain queued (#111).
  Retained updates on rows touched by that batch refresh ``row_version`` to
  the per-row post-save stamp (untouched rows keep their prior version).

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

## [0.12.0] — 2026-08-05

### Added

- Phase 0.12 data and visualization scale contracts and adapters.



## [0.11.0] — 2026-08-04

### Added
- Phase 0.11 native framework depth (Flask Blueprint/`init_app`, Django AppConfig/forms/QuerySet,
  portable adapter harness, HDJ manifests/CSP inventory, Celery/RQ bridges, live helpers).

### Fixed
- `DjangoQuerySetDataSource` deny-by-default allowlists when sort/filter lists are omitted.


## [0.10.1] — 2026-08-04

### Fixed
- Fail closed on unsupported SQLAlchemy `DataQuery.projection`.

## [0.10.0] — 2026-08-04

- Joined the coordinated 0.10 package train.

## [0.9.0] — 2026-08-04

- Joined the coordinated 0.9 package train and updated plugin compatibility metadata.

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


## [0.6.0] — 2026-08-03

- Async `VisualizationSource` protocol and viz row/payload defaults.
- `SQLAlchemyDataSource` adapter (`hedron-data[sqlalchemy]` / `[sqlmodel]`).
- AG Grid Community host shim and `ensure_aggrid_assets()` (`hedron-data[aggrid]`).
- Bounded SQLAlchemy paging: `OFFSET`/`LIMIT` applied in SQL (not collect-all-then-slice).

## [0.5.0] — 2026-08-03

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

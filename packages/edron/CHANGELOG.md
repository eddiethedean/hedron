# Changelog

## [1.0.2] — 2026-08-31

- Maintenance release for the coordinated 1.0 train.

## [1.0.1] — 2026-08-30

- Maintenance release for the coordinated 1.0 train.

## [1.0.0] — 2026-08-28

### Changed

- Require the Hedron and hedron-data 1.x trains (`>=1.0.0,<2.0`).
- Register Edron pages, fragments, actions, and feature bundles exclusively through Hedron's
  canonical 1.0 `page`, `view`, `action`, and `include` APIs.
- Delegate native handle construction, route synchronization, lifecycle metadata, result lowering,
  and application handle registration to Hedron instead of duplicating those responsibilities.
- Broaden Markdown to `>=3.4.1` and Uvicorn to `>=0.32`; set the verified Narwhals
  floor to `>=1.1` for Pandas, Polars, and PyArrow adapters.

## [0.9.1] — 2026-08-27

### Fixed

- Publish the Hedron 1.0-compatible dependency metadata under a new immutable
  patch version, including the corresponding charts and maps satellite floors.

## [0.9.0] — 2026-08-27

### Added

- Native Hedron 0.67 interaction, outcome, Alpine feature-plan, and fragment-closure exports.
- Demand-driven browser helpers, compatibility metadata, interaction explanation facts, and
  deprecated-path migration scanning.
- Phase 0.9 release, upgrade, compatibility, and native identity evidence.

### Changed

- Edron supports the Hedron 0.67 through 1.x compatibility range (`>=0.67.0,<2.0`)
  for both `hedron` and `hedron-data`.
- Edron page/action registration uses Hedron's canonical `view` and `action` surfaces.

## [0.8.0] — 2026-08-27

### Added

- Explicit local, single-process, reverse-proxy, container, orchestrated, Workbench, and Posit
  Connect deployment profiles with deterministic precedence and bounded diagnostics.
- `edron deploy-check` plus profile-aware `doctor` reports for production manifests, secrets,
  proxy trust, root paths, multi-worker state/job claims, and host handoffs.
- Deterministic Edron artifact manifests with bounded SHA-256 records for offline promotion and
  release verification.
- Phase 0.8 acceptance packet, profile/proxy/host/recovery fixtures, and deployment guide.

### Changed

- Scaffolds and generated migration projects pin the current `edron>=0.8,<0.9` package train.

## [0.7.0] — 2026-08-27

### Added

- Bounded, no-execution `edron migrate streamlit` analysis and Edron-native project generation.
- Deterministic JSON, text, and SARIF migration reports with source maps and a review checklist.
- Opt-in syntax-only codemods for safe Edron API spelling migrations.

## [0.6.0] — 2026-08-26

### Added

- Declarative `FeaturePackage` composition with native FeatureBundle inclusion, asset
  collision/deduplication, provenance, and rollback.
- Typed app-owned navigation targets and shared bounded layout recipes over native Hedron nodes.
- Reviewed lazy promotion metadata for the mature `hedron-data`, `hedron-charts`, and
  `hedron-maps` capabilities, with explicit native ejection guidance.
- Bounded deterministic application manifests and callback-free conformance reports.

## [0.5.0] — 2026-08-26

### Added

- App-owned native resource registration with lazy resolution, lifespan cleanup, health metadata,
  and explicit dependency descriptors.
- Native-backed Edron caching with TTL, scope/vary policy, tags, mutable-value isolation, and
  bounded per-function eviction.
- JobFlow backend selection, native poll policy wiring, bounded retry/result policy metadata, and
  safe native job-status SSE event formatting.
- Bounded deployment diagnostics and resource metadata through `App.operations()` and `doctor`.

### Fixed

- Edron JobFlow now honors its explicit backend and polling interval instead of silently using the
  process-global job backend/default poll policy.

## [0.4.0] — 2026-08-26

### Added

- Advanced native chart specifications with explicit accessible alternatives.
- Typed chart and map interaction registration that resolves Edron actions to native handles.
- Native image, audio, and video page helpers with safe URLs and validated media tracks.
- Bounded visualization interaction metadata in `App.explain()`.

### Fixed

- Edron action handlers now receive fresh request-local controller instances without permitting
  output emission during action execution.
- Chart and map interaction dispatch supports both native handlers and Edron action endpoints.

## [0.3.0] — 2026-08-26

### Added

- Explicit native, in-memory/dataframe, and SQLAlchemy data-source facades.
- Bounded data workspaces with allowlisted paging, filters, sorting, search, selection, and CSV
  export.
- Typed edit intents with deny-by-default authorization, validation, writable-field, concurrency,
  and value-free audit contracts.
- Native DataTable/DataEditor page composition and ordinary-form DataWorkspace escape hatch.

## [0.2.0] — 2026-08-26

### Added

- Source-aware structured diagnostics and AST-only `check` tooling.
- Bounded application explanations, source maps, capability doctor, and SARIF reports.
- `edron new` minimal, dashboard, and form teaching scaffolds.
- Explicit `function_page`/`page_function` and `inherit`/`expose` authoring conveniences.

## [0.1.0] — 2026-08-26

### Added

- Initial Edron class-oriented authoring facade over Hedron.

### Fixed

- Lowered fragment/action dependencies into their native route registrations.
- Preserved explicitly bound action arguments in generated controls and forms.

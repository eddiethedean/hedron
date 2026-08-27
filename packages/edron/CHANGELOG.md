# Changelog

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

# Changelog

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
- `reconcile_csp` fails closed when CSP is missing or lacks `script-src` for eval/inline caps.


## [0.10.1] - 2026-08-04

### Fixed
- Reject generic `|safe` / `autoescape false` even when `strict=False`.

## [0.10.0] - 2026-08-04

### Added
- `two_phase_stream()` metadata-first streaming API; version-aware unknown `hx-*` diagnostics (HED-JINJA-0027); registered fragment head-management path for `htmx-ext-head-support`.

## [0.9.0] - 2026-08-04

- Replace the removed HDN language with HDJ, an explicit standards-first `.hdj` format whose static
  prologue declares template kind, feature profile, and required capabilities before a Jinja body.
- Add typed template specifications, explicit component bindings, component/body/slot tags,
  one shared core render session, and HTML-body/purpose-specific URL trust filters.
- Add the mandatory prologue parser, `.hdj`-only guarded loader, static dependency/kind checks,
  capability-versus-policy diagnostics, registered assets, and bounded chunk consumption.
- Reject direct rendering, dynamic/foreign format-v1 dependencies, conditional page assets, and
  public `Template.stream()` paths; later-phase ownership is recorded in RFC-0031 and the roadmap.
- Close format-v1 evidence for profiles, sinks, HTMX local checks, composition parity, progressive
  examples, and the 0.8→0.9 manual upgrade fixture.

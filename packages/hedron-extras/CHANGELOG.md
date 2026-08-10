# Changelog

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

### Changed

- Coordinated Beta patch with `hedron` 0.25.2 (docs honesty + package train alignment).

## [0.25.1] — 2026-08-09

### Fixed

- Require `hedron-charts>=0.1.6,<0.2` for the chart workbench so the extra cannot
  resolve to a chart wheel built for an older Hedron core.

## [0.25.0] — 2026-08-09

### Changed

- Coordinated Beta train bump with `hedron` 0.25.0.
- **EXTRAS-025 quarantine:** `CodeEditor`, `TerminalView`, `Joystick`, and `DeviceBridge`
  move behind `hedron[experimental-ui]` / `hedron_extras.experimental`. Curated
  `hedron[extras]` no longer registers or re-exports those landmines.

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

### Changed

- Coordinated Beta train with phase 0.19 accessibility engineering (see `hedron-core` /
  `hedron` / `hedron-explorer` changelogs for capability detail).


## [0.18.0] — 2026-08-06

### Changed

- Coordinated Beta train with phase 0.18 model demos / inference workflows.


## [0.17.0] — 2026-08-06

### Changed

- Coordinated Beta train with phase 0.17 (`hedron-core>=0.17.0,<0.18`).

## [0.16.0] — 2026-08-06

### Added

- Initial Beta release of curated extras: composition UI, analysis workbenches,
  CodeEditor/JSONEditor, image tools, calendar/signature/typeahead, display
  recipes, browser-Python sandbox, and Experimental specialty extras
  (TerminalView, joystick/device recipes).
- Per-feature capability manifests via `PluginContext.register_feature`.

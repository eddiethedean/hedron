# Changelog

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

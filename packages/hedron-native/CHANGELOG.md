# Changelog

## [0.42.0] — 2026-08-14

### Added
- Phase 0.42 production-grade Web Component platform graduation (D-070).

### Changed
- Coordinated train tip `0.42.0` (in-tree cut; tag/PyPI deferred).

## [0.1.2] — 2026-08-10

### Fixed

- Honor `HEDRON_NATIVE_DISABLE` on every `escape_*` / `native_available()` call so
  ops can force the Python-reference path without process restart (NATIVE-028).

### Changed

- Cargo / PyPI version bump so the live-disable fix is installable (PyPI `0.1.1`
  remains immutable).

## [0.1.1] — 2026-08-10

### Added

- `HEDRON_NATIVE_DISABLE` runtime disable for Python-reference fallback (NATIVE-028).
- cibuildwheel Supported matrix (manylinux x86_64/aarch64, macOS arm64, Windows amd64).
- Fuzz corpus + sanitize evidence packet under `docs/acceptance/native-fuzz-028/`.

### Changed

- Package maturity Alpha → **Beta**.
- Cargo crate is publishable to crates.io (`0.1.1`); `extension-module` is a maturin-only feature.

## [0.1.0] — 2026-08-05

### Added

- Optional PyO3 extension providing `escape_text` / `escape_attr` with automatic
  pure-Python fallback when the native module is unavailable.
- PyO3 0.27 for CPython 3.11–3.14 support.

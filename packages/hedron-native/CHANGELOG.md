# Changelog

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

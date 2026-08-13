## [0.35.0] — 2026-08-13

### Added

- Coordinated Beta train cut for whole-fleet production-grade closure (D-063 / RFC-0068).

## [0.34.0] — 2026-08-13

### Added

- Coordinated Beta train cut for production-grade Gradio client interop (D-062 / RFC-0067).
- Native Connect GUID path Supported on Connect **2025.06.0** (in addition to 2026.07.0).
  `hedron-posit` ships a `pkg_resources.parse_version` shim so Connect 2025.06 FastAPI
  workers start under setuptools 82+.

# Changelog

## [0.33.0] — 2026-08-13

- Initial `hedron-posit` Beta distribution: `HedronPosit` facade with nested
  `PositConfig` / `ConnectConfig` / `PositProduct` / `ConnectCookieMode`.
- One-way dependency on `hedron` + `fastapi-workbench`; `hedron-workbench` becomes
  a thin compatibility subclass package.
- Native Connect GUID path Supported on Connect 2026.07.0; request cookies unchanged.
- `ConnectCookieMode.authenticated_header_v1` fails closed (`HED-POSIT-0401`);
  Stage 0 `BRIDGE_DECISION=drop_supported`.
- CLI `hedron-posit run` / `check` / `doctor` with `posit_status` diagnostics.

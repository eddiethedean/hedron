# Changelog

## [1.0.4] — 2026-09-01

- Maintenance release for the coordinated 1.0 train.

## [1.0.3] — 2026-08-31

### Security
- Require protected Connect runtime evidence before trusting native forwarded headers, and
  expand secret redaction across structured and free-form diagnostics.

### Changed
- Share launcher and CLI resolution primitives with `fastapi-workbench>=1.0.3` and add
  cross-package conformance coverage for mounts, origins, paths, and cookie scope.

## [1.0.2] — 2026-08-31

### Fixed
- Require `fastapi-workbench>=1.0.2`, the first published artifact containing the
  `absolute_redirects` middleware contract used by `HedronPosit`.
- Add installed-wheel compatibility coverage for Workbench startup, full-URL mount resolution,
  and middleware construction.

## [1.0.1] — 2026-08-30

- Maintenance release for the coordinated 1.0 train.

### Yanked
- Yanked from PyPI on 2026-09-01 because its declared
  `fastapi-workbench>=1.0.1,<2.0` range permits 1.0.1, which does not provide the
  `absolute_redirects` middleware contract required by `HedronPosit`.

## [1.0.0] — 2026-08-27

- Align Posit package metadata with the Hedron 1.0 coordinated train.
- Broaden direct Starlette compatibility to `>=0.40.0`.

### Yanked
- Yanked from PyPI on 2026-09-01 because its declared
  `fastapi-workbench>=1.0.1,<2.0` range permits 1.0.1, which does not provide the
  `absolute_redirects` middleware contract required by `HedronPosit`.

## [0.67.1] — 2026-08-28

### Fixed
- Preserve the external Workbench origin when `UVICORN_ROOT_PATH` contains a full
  session URL (#747).
- Remove `UVICORN_ROOT_PATH` before supervised reload/worker handoff so Uvicorn
  cannot interpret the full Workbench URL as an ASGI `root_path` (#748).

### Changed
- Require Hedron `>=0.67.0`.

## [0.67.0] — 2026-08-27

### Changed
- Aligned the Posit facade and coordinated package metadata with the Phase 0.67 release train.

### Yanked
- Yanked from PyPI on 2026-09-01 because full-URL `UVICORN_ROOT_PATH` values lost the
  external Workbench origin and leaked into reload/worker Uvicorn supervision. Use 0.67.1
  or a supported 1.0.x release.

## [0.66.2] — 2026-08-26

### Fixed
- Maintenance fixes for the 0.66.x release train.

## [0.66.1] — 2026-08-25

### Fixed
- Maintenance fixes for the 0.66.x release train.

## [0.66.0] — 2026-08-25

### Changed
- Coordinated development train for Phase 0.66 HDJ parity and registry integration.

## [0.65.0] — 2026-08-25

### Added
- Integrated application styling platform: registered custom CSS, cascade layers, stable hooks, bounded recipes, diagnostics, and provenance-preserving ejection.

### Fixed
- Added trusted scheme-absolute Workbench redirects for proxy deployments that
  rewrite path-absolute `Location` headers.

### Changed
- Coordinated train cut for Phase 0.65.
- Consolidated the Workbench resolver, middleware, and launcher on the shared
  `fastapi-workbench` core; Hedron-Posit retains only its branding and Connect
  composition layer.

## [0.64.1] — 2026-08-25

### Fixed
- Maintenance fixes for the 0.64.x release train.

## [0.64.0] — 2026-08-24

### Added
- 0.64 presentation and HTMX lifecycle compatibility for Posit hosts.

## [0.63.0] — 2026-08-24

### Changed
- Coordinated Phase 0.63 release metadata and theme bundle integration.

## [0.62.0] — 2026-08-24

### Changed
- Coordinated train cut for phase 0.62 navigation, optimism, failure isolation, and identity contracts.

## [0.61.0] — 2026-08-24

### Changed
- Adopted the 0.62 coordinated train for Posit deployment boundaries and action-state metadata.

## [0.60.2] — 2026-08-24

### Fixed
- Corrected Workbench mount handoff for full `rserver-url` URLs and mismatched listener ports.
- Preserved resolved Connect runtime evidence when validating native app base URLs.

### Changed
- Coordinated train tip `0.61.0` (in-tree patch; tag/PyPI published).

## [0.60.1] — 2026-08-23

### Fixed
- Bug fixes from the 0.60.1 maintenance release.

### Changed
- Coordinated train tip `0.61.1` (in-tree patch; tag/PyPI deferred).

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

## [0.53.0] — 2026-08-20

### Added

- Coordinated train tip `0.53.0` (in-tree Published; tag/PyPI deferred).
- Application DX contracts (RFC-0080 / D-091 / D-092): assets, diagnostics, routes,
  workflows, testgen, theming, discovery, and fleet doctor.

## [0.52.0] — 2026-08-20

### Changed
- Coordinated train tip `0.52.0` (in-tree Published; tag/PyPI deferred).
- Phase 0.52 conformance authority + Posit lifecycle (RFC-0079 / D-089 / D-090; #522).
- Posit lifecycle: `PositContext`, `CookieRegistry`, `hands_off`, matrix check, diagnostics, query/fragment parity (#508–#513).

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

## [0.50.0] — 2026-08-18

### Changed
- Coordinated train tip `0.50.0` (in-tree cut; tag/PyPI deferred).

### Added
- Explorer architecture services/views split, ExplorerProvider v1, query pagination,
  diffs, headless CLI parity, bounded lab, and HTMX authoring primitives (#496–#500, #502, #503).

## [0.49.1] — 2026-08-18

### Changed
- Coordinated train tip `0.49.1` (in-tree patch; tag/PyPI deferred).

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

## [0.46.0] — 2026-08-16

### Added
- Coordinated train tip; host exceptions unchanged.

### Changed
- Coordinated train tip `0.46.0`.


## [0.45.0] — 2026-08-16

### Added
- Phase 0.45 mount-aware production interactions.json validation.

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
- Native Connect GUID path Supported on Connect **2025.06.0** (in addition to 2026.07.0).
  `hedron-posit` ships a `pkg_resources.parse_version` shim so Connect 2025.06 FastAPI
  workers start under setuptools 82+.

## [0.33.0] — 2026-08-13

- Initial `hedron-posit` Beta distribution: `HedronPosit` facade with nested
  `PositConfig` / `ConnectConfig` / `PositProduct` / `ConnectCookieMode`.
- One-way dependency on `hedron` + `fastapi-workbench`; `hedron-workbench` becomes
  a thin compatibility subclass package.
- Native Connect GUID path Supported on Connect 2026.07.0; request cookies unchanged.
- `ConnectCookieMode.authenticated_header_v1` fails closed (`HED-POSIT-0401`);
  Stage 0 `BRIDGE_DECISION=drop_supported`.
- CLI `hedron-posit run` / `check` / `doctor` with `posit_status` diagnostics.

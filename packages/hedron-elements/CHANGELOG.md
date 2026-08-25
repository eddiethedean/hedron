# Changelog

## [0.64.0] — 2026-08-24

### Added
- 0.64 presentation metadata and lifecycle compatibility for supported elements.

## [0.63.0] — 2026-08-24

### Added
- Registry-derived component parts, slots, state hooks, metadata, and state-matrix evidence.

## [0.62.0] — 2026-08-24

### Added
- Opt-in generation-safe navigation enhancement with ordinary-link fallback, safe prefetch, and
  capability-detected View Transitions.

## [0.61.0] — 2026-08-24

### Added
- Canonical action lifecycle markers and stale-generation protection for supported async elements.

## [0.60.2] — 2026-08-24

### Fixed
- Coordinated Workbench and Connect integration fixes from the 0.60.2 maintenance release.

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
- Frozen markup keeps FieldFile / FieldText / FieldChoice ABI attributes and Disclosure / Dialog `open`.
- `ActionAsync` accepts and emits `hx-target`.

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
- Form-associated ``hedron-field-*`` elements drop inner ``name`` so light-DOM controls do not double-submit (#399).
- Reconnect aborts prior DOM listeners on bridge, disclosure, and async-action elements (#276).
- Draft transfer forbids exact sensitive field names, not substrings such as ``secretary`` (#259).
- ``ActionAsync`` validates ``hx-post`` as a form-action URL (#257).
- ``enhanceNavigation`` listener registration is idempotent (#280).

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
- Opt-in schema-aware generate_form(enhance='elements'); native forms remain canonical.

### Changed
- Coordinated train tip `0.46.0`.


## [0.45.0] — 2026-08-16

### Added
- Phase 0.45 current-surface PackageProjection; direct element APIs remain usable without a catalog.

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

### Fixed
- ``CompositionEdge.as_payload`` emits camelCase keys the JS runner reads, and
  ``concurrency="queue"`` serializes overlapping dispatches (#256).
- Draft transfer Python helpers mint the same ``sessionStorage`` key and camelCase
  millisecond envelope as ``composition-041.mjs`` (#255).

## [0.41.0] — 2026-08-15

- Typed allowlisted browser composition with bounded graph execution and native fallback.
- Subject-bound, session-scoped, single-consume draft transfer with strict clearing and ceilings.
- Progressive fragment navigation, metadata-only traces, and per-element failure isolation.

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

### Fixed

- `render_element_markup` rejects `style=` except the `--hedron-gap` layout
  allowlist, and runs `href` / `src` / `formaction` / `poster` / `srcset` /
  HTMX URL attributes through `SafeUrl` so `vbscript:`, `data:`, `file:`, and
  `javascript:` cannot be emitted (#244).

## [0.36.0] — 2026-08-13

- Initial Alpha release: element ABI registry integration, shared bridge, and
  `hedron-example` reference light-DOM element (RFC-0060 / D-064).

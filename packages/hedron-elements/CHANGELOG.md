# Changelog

## [0.42.0] - 2026-08-14

### Added
- Phase 0.42 production-grade Web Component platform graduation (D-070).

### Changed
- Coordinated train tip `0.42.0` (in-tree cut; tag/PyPI deferred).

## [0.41.0] — Unreleased

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

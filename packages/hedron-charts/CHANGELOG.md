# Changelog

## [0.1.6] — 2026-08-09

### Fixed

- Publish the first chart satellite compatible with `hedron-core>=0.25.0,<0.26`,
  restoring the `hedron[charts]>=0.27.0,<0.28` installation path.
- Replace the repository-only missing-extra diagnostic with valid PyPI install commands.

## [0.1.5] — 2026-08-07

### Changed

- Pin `hedron-core` to `>=0.25.0,<0.26` for the living Beta train (workspace pin;
  earlier notes targeting `0.20` / `0.19` are superseded).

## [0.1.4] — 2026-08-06

### Changed

- Pin `hedron-core` to `>=0.18.0,<0.19` for the 0.18 train.

## [0.1.3] — 2026-08-05

### Changed

- Pin `hedron-core` to `>=0.16.0,<0.17` for the 0.16 train.

## [0.1.2] — 2026-08-05

### Changed

- Pin `hedron-core` to `>=0.14.0,<0.15` for the 0.14 train.

## [0.1.1]

- Offline fingerprinted Plotly/Vega/Chart.js runtimes, optional adapter hosts,
  beginner Area/Bar/Scatter fixes, and D-047 CSP-safe map/chart contracts.
 — 2026-08-05

### Changed

- Pin `hedron-core` to `>=0.13.0,<0.14` for the 0.13 train.



## [0.1.0] — 2026-08-05

### Changed
- Version independently as Alpha (`0.1.x`); no longer locked to the Beta package train.
- Compatible with `hedron-core>=0.11.0,<0.12`.



## [0.10.1] - 2026-08-04

### Fixed
- Re-validate Matplotlib `render_node` SVG/PNG bodies before trusted emission.
- Treat chart `data:` URLs as disallowed remote assets.

## [0.10.0] - 2026-08-04

- Joined the coordinated 0.10 package train.
- Raise the Altair optional extra to `>=6.0,<7` for Python 3.14 TypedDict compatibility.

## [0.9.0] - 2026-08-04

- Joined the coordinated 0.9 package train and updated plugin compatibility metadata.

## [0.8.0] - 2026-08-03

### Added

- Public stability catalog, deprecation/semver policy, upgrade guide, and threat model.
- Performance budgets with enforcement tests; three-engine browser HTMX matrix scaffolding.
- SBOM, license inventory, browser-asset audit, and release evidence bundle scripts.
- Flask/Django hardening suites and Django Supported floor `>=5.2,<6`.

### Changed

- Feature freeze: no new subsystems, adapters, or transports on the 0.8 train.

## [0.7.0] — 2026-08-03

- Phase 0.7 portable adapters, operations, and jobs train.


## [0.6.0] - 2026-08-03

- Initial `hedron-charts` package: `VisualizationAdapter` implementations for
  Matplotlib, Plotly, and Altair/Vega-Lite; beginner `LineChart`; accessibility
  title/description/alt/waiver contracts; payload/row limits; local host shims;
  Auto renderer registration; Explorer visualization panel.
- Adversarial rejection of executable callbacks, remote CDN URLs, and active SVG
  content; host shims fail closed when Plotly/vegaEmbed globals are missing.
- Interactive Plotly/Vega **full offline runtime pin/fingerprint** is Deferred /
  experimental (`VIS-C06-002`); applications may supply pinned local runtimes.

[0.6.0]: https://github.com/eddiethedean/hedron/releases/tag/v0.6.0

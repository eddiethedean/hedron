# Changelog

## [0.43.0] — 2026-08-16

### Changed
- Coordinated train tip `0.43.0` (in-tree cut; tag/PyPI deferred).

### Fixed
- ``ChartInteraction`` materializes an event command that posts the typed payload
  to the bound ActionHandle, instead of only a dummy export stub (#341).

## [0.42.0] — 2026-08-14

### Added
- Phase 0.42 production-grade Web Component platform graduation (D-070).

### Changed
- Coordinated train tip `0.42.0` (in-tree cut; tag/PyPI deferred).

### Fixed
- ``hedron-chart`` removes its keydown listener in ``cleanup`` so remounts do not
  stack handlers (#270).

## [0.2.0] — 2026-08-14

### Added
- `ChartInteraction` compiles Supported chart events onto ActionHandle effects; core pin `>=0.46.0,<0.47`.


- Phase 0.38 high-fidelity charts / train alignment (D-066 / RFC-0069).


## [0.1.11] — 2026-08-11

### Fixed

- Chart hosts also listen for ``htmx:oobBeforeSwap`` / ``htmx:oobAfterSwap`` and
  ``htmx:load`` so OOB swaps dispose and remount correctly.
- Plotly and Vega ignore stale async ``then`` callbacks after remount/destroy
  (generation token).
- MapLibre honors ``coord_order`` (``latlng`` Folium vs ``lnglat`` native) and
  ignores GeoJSON ``load`` handlers after destroy.
- Mermaid initializes once per page; Chart.js keeps the instance on the host
  element for reliable destroy.

## [0.1.10] — 2026-08-11

### Fixed

- Plotly and Vega hosts call ``destroy`` at the start of ``mount`` so remounts without
  a prior HTMX dispose do not stack handlers or leak views.

### Changed

- Pin ``hedron-core`` to ``>=0.28.2,<0.29``.

## [0.1.9] — 2026-08-10

### Fixed

- Chart hosts dispose and remount when the HTMX swap target is the host element
  itself (`matches` + `querySelectorAll`), not only descendants.
- Register HTMX lifecycle listeners on `document` (avoid `document.body &&` races).

### Changed

- Pin `hedron-core` to `>=0.28.1,<0.29`.
- Auto chart-stub remediation points adopters at Experimental opt-in (`as_`) instead
  of an install-only message for Plotly/Altair.

## [0.1.8] — 2026-08-10

### Added

- Production-grade Supported inventory for Matplotlib/static beginner charts
  (CHARTS-028); Plotly/Altair remain Experimental and excluded from Auto defaults
  (INTERACTIVE-028).

### Changed

- Package maturity Alpha → **Beta**.
- Pin `hedron-core` to `>=0.28.0,<0.29`.
- Expand `RUNTIME_PINS` digests for Experimental echarts/mermaid/maplibre hosts.
- Plotly/Vega hosts purge on `htmx:beforeSwap`.

## [0.1.7] — 2026-08-10

### Changed

- Pin `hedron-core` to `>=0.27.0,<0.28` for the living Beta train.
- Document the release as **0.27-compatible** (supersedes the mistaken 0.25 wording on `0.1.6`).

## [0.1.6] — 2026-08-09

### Fixed

- Publish a chart satellite compatible with the living Hedron train (workspace pin
  `hedron-core>=0.27.0,<0.28` on the 0.27 cut; earlier draft notes mentioning
  `>=0.25.0,<0.26` were incorrect for that wheel).
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



## [0.10.1] — 2026-08-04

### Fixed
- Re-validate Matplotlib `render_node` SVG/PNG bodies before trusted emission.
- Treat chart `data:` URLs as disallowed remote assets.

## [0.10.0] — 2026-08-04

- Joined the coordinated 0.10 package train.
- Raise the Altair optional extra to `>=6.0,<7` for Python 3.14 TypedDict compatibility.

## [0.9.0] — 2026-08-04

- Joined the coordinated 0.9 package train and updated plugin compatibility metadata.

## [0.8.0] — 2026-08-03

### Added

- Public stability catalog, deprecation/semver policy, upgrade guide, and threat model.
- Performance budgets with enforcement tests; three-engine browser HTMX matrix scaffolding.
- SBOM, license inventory, browser-asset audit, and release evidence bundle scripts.
- Flask/Django hardening suites and Django Supported floor `>=5.2,<6`.

### Changed

- Feature freeze: no new subsystems, adapters, or transports on the 0.8 train.

## [0.7.0] — 2026-08-03

- Phase 0.7 portable adapters, operations, and jobs train.


## [0.6.0] — 2026-08-03

- Initial `hedron-charts` package: `VisualizationAdapter` implementations for
  Matplotlib, Plotly, and Altair/Vega-Lite; beginner `LineChart`; accessibility
  title/description/alt/waiver contracts; payload/row limits; local host shims;
  Auto renderer registration; Explorer visualization panel.
- Adversarial rejection of executable callbacks, remote CDN URLs, and active SVG
  content; host shims fail closed when Plotly/vegaEmbed globals are missing.
- Interactive Plotly/Vega **full offline runtime pin/fingerprint** is Deferred /
  experimental (`VIS-C06-002`); applications may supply pinned local runtimes.

[0.6.0]: https://github.com/eddiethedean/hedron/releases/tag/v0.6.0

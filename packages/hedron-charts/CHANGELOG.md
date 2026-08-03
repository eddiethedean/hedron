# Changelog

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

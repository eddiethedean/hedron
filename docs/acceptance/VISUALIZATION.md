# Visualization acceptance

## Adapters

- [x] Matplotlib static output, Plotly interactive JSON, and Altair/Vega-Lite specifications follow
  one lifecycle contract. *(unit/adapter evidence; interactive browser runtime pin Deferred as
  `VIS-C06-002`)*
- [x] Optional packages are lazy and missing dependencies produce exact installation commands.
- [ ] ~~Browser runtimes pinned/fingerprinted/offline~~ — **Deferred** (`VIS-C06-002`): host shims
  fail closed; apps may supply runtimes; first-party pin/fingerprint remains 0.6.x maintenance /
  0.7 evidence before advertising as supported.
- [x] Payload and row limits prevent accidental large browser transfers.
- [x] Raw executable callbacks, unapproved remote resources, and active content in chart/SVG
  fallback paths are rejected by an adversarial corpus. *(`VIS-C06-001` /
  `tests/security/test_chart_svg_corpus.py`)*

## Accessibility and diagnostics

- [x] Every chart has a title and description or explicit waiver.
- [x] Static charts require alt text or description/waiver; supported simple charts offer tabular
  fallback (`LineChart` / Matplotlib adapter).
- [ ] Color, keyboard, focus, and screen-reader behavior meet the chart contract in a real browser.
  *(beyond Chromium HTMX smoke; track with a11y matrix)*
- [ ] Explorer shows backend, specification, data schema, redaction, size, timing, assets, caching,
  and fallback with evidence linked under [EVIDENCE.md](EVIDENCE.md).

## Exit

Matplotlib / `LineChart` path is verified for 0.6 closure. Interactive Plotly/Vega offline runtime
pinning is explicitly Deferred (`VIS-C06-002`). See [release-gate-0.6.toml](release-gate-0.6.toml).

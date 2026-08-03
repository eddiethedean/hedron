# Visualization acceptance

## Adapters

- [ ] Matplotlib static output, Plotly interactive JSON, and Altair/Vega-Lite specifications follow
  one lifecycle contract with real-browser evidence. *(implementation shipped; closure evidence open)*
- [x] Optional packages are lazy and missing dependencies produce exact installation commands.
- [ ] Browser runtimes, not only host shims, are pinned, fingerprinted, locally served,
  deduplicated, and exercised offline. *(0.6 closure gate)*
- [x] Payload and row limits prevent accidental large browser transfers.
- [ ] Raw executable callbacks, unapproved remote resources, and active content in chart/SVG
  fallback paths are rejected by an adversarial corpus. *(0.6 closure gate)*

## Accessibility and diagnostics

- [x] Every chart has a title and description or explicit waiver.
- [ ] Static charts require alt text; supported simple charts offer tabular fallback.
- [ ] Color, keyboard, focus, and screen-reader behavior meet the chart contract in a real browser.
- [ ] Explorer shows backend, specification, data schema, redaction, size, timing, assets, caching,
  and fallback with evidence linked under [EVIDENCE.md](EVIDENCE.md).

## Exit

All three initial adapters render in the reference application under strict CSP and private
authenticated caching without leaking secret columns. The exit remains open until every requirement
above is `Verified` under [EVIDENCE.md](EVIDENCE.md).

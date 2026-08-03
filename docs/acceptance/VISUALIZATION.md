# Visualization acceptance

## Adapters

- [ ] Matplotlib static output, Plotly interactive JSON, and Altair/Vega-Lite specifications follow one lifecycle contract.
- [ ] Optional packages are lazy and missing dependencies produce exact installation commands.
- [ ] Browser runtimes are pinned, fingerprinted, locally served, and deduplicated.
- [ ] Payload and row limits prevent accidental large browser transfers.
- [ ] Raw executable callbacks and unapproved remote resources are rejected.

## Accessibility and diagnostics

- [ ] Every chart has a title and description or explicit waiver.
- [ ] Static charts require alt text; supported simple charts offer tabular fallback.
- [ ] Color, keyboard, focus, and screen-reader behavior meet the chart contract.
- [ ] Explorer shows backend, specification, data schema, redaction, size, timing, assets, caching, and fallback.

## Exit

All three initial adapters render in the reference application under strict CSP and private authenticated caching without leaking secret columns.


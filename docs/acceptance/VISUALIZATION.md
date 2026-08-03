# Visualization acceptance

## Adapters

- [x] Matplotlib static output, Plotly interactive JSON, and Altair/Vega-Lite specifications follow one lifecycle contract.
- [x] Optional packages are lazy and missing dependencies produce exact installation commands.
- [x] Browser runtimes are pinned, fingerprinted, locally served, and deduplicated.
- [x] Payload and row limits prevent accidental large browser transfers.
- [x] Raw executable callbacks and unapproved remote resources are rejected.

## Accessibility and diagnostics

- [x] Every chart has a title and description or explicit waiver.
- [x] Static charts require alt text; supported simple charts offer tabular fallback.
- [x] Color, keyboard, focus, and screen-reader behavior meet the chart contract.
- [x] Explorer shows backend, specification, data schema, redaction, size, timing, assets, caching, and fallback.

## Exit

All three initial adapters render in the reference application under strict CSP and private authenticated caching without leaking secret columns.

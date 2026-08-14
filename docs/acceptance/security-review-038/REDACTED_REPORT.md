# Security review — phase 0.38 (redacted)

**Package / train at cut:** Hedron `v0.38.0` + Beta `hedron-charts` `0.2.0`  
**Owning RFC:** RFC-0069 · **Gate:** `SECURITY-038` · **Tracking:** #251  
**Reviewer:** maintainer-led (2026-08-14)

## Findings

No open critical or high findings for 0.38 scope.

| ID | Severity | Summary | Disposition |
|---|---|---|---|
| CH-038-01 | info | ChartSpec rejects unknown fields, schema versions, and prototype-pollution keys | accepted |
| CH-038-02 | info | Closed transform operator catalog; no JS callbacks (#75) | accepted — fixed |
| CH-038-03 | info | SVG/active-markup scanner strips NUL and rejects remote `@import` / SMIL href (#81/#201/#239) | accepted — fixed |
| CH-038-04 | info | Export paths require authorization and redact secret fields | accepted |
| CH-038-05 | low | First-party renderer embeds D3-inspired algorithms; vendor adapters remain Experimental | accepted — documented |
| CH-038-06 | info | Host generation guards purge stale Plotly/Mermaid mounts (#71/#72) | accepted — fixed |

## Adversarial coverage exercised

- Prototype pollution and unknown ChartSpec fields
- Formatter / HTML event-handler callback strings
- NUL-split SVG tags, remote CSS `@import`, SMIL remote href mutation
- Unauthorized export and oversized dimensions
- Negative `max_points` downsample defeat (#83)
- Tabular fallback row retention (#82)

## Residual risk

`hedron-elements` remains incubator until 0.42. Live SSE/WS remain experimental. Scoped AT-038 is not Supported human AT (`SR-021`).

## Supply

- Reproducible local assets under `hedron_charts/static/`
- No consumer Node dependency
- SBOM: [SBOM.json](SBOM.json)

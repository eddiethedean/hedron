# Upgrade fixtures — phase 0.36 (Web Component ABI)

Baseline: Published **`v0.35.0`**. Cut: **`v0.36.0`**.

Pins at cut: `hedron>=0.36.0,<0.37` and optional Alpha
`hedron-elements>=0.36.0,<0.37`.

## Goldens / suites

- ABI schema fixtures for registry records and frozen markup (`hedron-example`)
- Lifecycle corpus: ≥100 outer / authorized inner / OOB / history cycles on one reference element
- SSR JS-off / failed-module / ABI-mismatch fallback cases
- State-ownership conflict fixtures (`HED-ELEMENT-STATE-*`)
- Host matrices: FastAPI / Flask / Django mounting of `hedron-elements` assets

## Pin migration (at cut)

| From tip | Historical pin | At 0.36 cut |
|---|---|---|
| `v0.35.0` | `hedron>=0.35.0,<0.36` | `hedron>=0.36.0,<0.37` |
| New | — | `hedron-elements>=0.36.0,<0.37` (Alpha) |

Independent satellites stay on their own lines (`hedron-mcp` / `hedron-gradio` `>=0.2.0,<0.3`,
`hedron-charts` / tooling `0.1.x`, `fastapi-workbench` `>=1,<2`).

## Fleet inventory amendment (post-0.35 Alpha)

At `v0.36.0` cut, append `hedron-elements` to the living fleet inventory without reopening
`FLEET-035`:

| Field | Value |
|---|---|
| Package | `hedron-elements` |
| Owner | `hedron` |
| Maturity | Alpha |
| Disposition | `incubator` |
| Compatibility | `hedron-core>=0.36.0,<0.37` |
| Channel | coordinated train Alpha |
| Production-grade destination | phase **0.41** |

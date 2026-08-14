# Upgrade fixtures — phase 0.37 (form-associated elements and interactive primitives)

Baseline: Published **`v0.36.0`**. Cut: **`v0.37.0`**.

Pins at cut: `hedron>=0.37.0,<0.38` and Alpha
`hedron-elements>=0.37.0,<0.38`.

## Goldens / suites

- Form parity corpus: native navigation vs HTMX across `hedron-field-text`,
  `hedron-field-choice`, `hedron-field-file` on FastAPI / Flask / Django
- Validity fixtures: ElementInternals + native fallback, constraint validation,
  server-returned 422 field errors, CSRF, labels/descriptions, reset/restore
- `InteractionState` concurrency matrix: drop/replace/queue/parallel, late response,
  retry, timeout, cancel, HTTP 202 vs job completion, disconnect
- Primitive catalog fixtures: disclosure, dialog, tabs, menu/popover, selection,
  bounded upload — keyboard, focus, semantic fallback, native-first review
- `GestureOverlayCatalog` fixtures: reorder/drag-drop, resize/splitter, pointer capture,
  overlay top-layer/focus/dismissal, allowlist violations, swap/disconnect cleanup
- HTMX matrices: inner/outer/OOB swaps, 422 fragments, duplicate submit, history restore,
  slow/canceled requests — values, errors, focus, authority preserved
- Human AT packet: representative keyboard-only and screen-reader form/primitive sessions
- Regression: 0.36 ABI evidence (`hedron-example`) must remain green alongside 0.37 suites
- High-severity remediations: #230–#237 closed (see [RELEASE_0_37](RELEASE_0_37.md))

## Pin migration (at cut)

| From tip | Historical pin | At 0.37 cut |
|---|---|---|
| `v0.36.0` | `hedron>=0.36.0,<0.37` | `hedron>=0.37.0,<0.38` |
| `v0.36.0` | `hedron-elements>=0.36.0,<0.37` | `hedron-elements>=0.37.0,<0.38` |

Independent satellites stay on their own lines (`hedron-mcp` / `hedron-gradio` `>=0.2.0,<0.3`,
`hedron-charts` / tooling `0.1.x`, `fastapi-workbench` `>=1,<2`).

## Fleet inventory amendment (post-0.36 Alpha)

At `v0.37.0` cut, update the `hedron-elements` row in the living fleet inventory without
reopening `FLEET-035`:

| Field | Value |
|---|---|
| Package | `hedron-elements` |
| Owner | `hedron` |
| Maturity | Alpha |
| Disposition | `incubator` |
| Compatibility | `hedron-core>=0.37.0,<0.38` |
| Channel | coordinated train Alpha |
| Production-grade destination | phase **0.42** |

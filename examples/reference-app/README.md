# Hedron reference application (phase 0.6)

Cumulative authenticated team-administration application demonstrating the published
0.6 train:

- `Hedron()` and plain `FastAPI` + `HedronRouter` modes
- Lazy addressable `UserTable` protected by router dependencies
- Typed create/update/delete actions with CSRF validation
- HTMX fragment swaps and bundled HTMX 2.0.10
- DataEditor, Auto, cache helpers, and ColorMode (phase 0.5)
- Charts (`LineChart`), Markdown, typed `InteractionResult`, declared fragment regions,
  and `/charts/*` interaction routes (phase 0.6)
- Offline static rendering helpers retained from phase 0.1

## Run

```bash
uv sync
uv run uvicorn app:app --app-dir examples/reference-app
```

Default credentials: `admin` / `secret` (HTTP Basic).

Open the home page for CRUD + DataEditor + the phase-06 chart/Markdown section. Chart
interaction endpoints live under `/charts/*` (for example `/charts/fragment`,
`/charts/search`).

## Tests

```bash
uv run pytest examples/reference-app tests/integration -q
```

Optional extras used by the phase-06 section (`charts`, `markdown`, sanitizer) are part
of the workspace sync; when developing against a minimal install, add
`hedron[charts]`, `hedron[markdown]`, and a chart backend such as
`hedron-charts[matplotlib]`.

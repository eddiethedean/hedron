# Hedron reference application (phase 0.2)

Authenticated team-administration CRUD application demonstrating:

- `Hedron()` and plain `FastAPI` + `HedronRouter` modes
- Lazy addressable `UserTable` protected by router dependencies
- Typed create/update/delete actions with CSRF validation
- HTMX fragment swaps and bundled HTMX 2.0.10
- Offline static rendering helpers retained from phase 0.1

## Run

```bash
uv sync
uv run uvicorn app:app --app-dir examples/reference-app
```

Default credentials: `admin` / `secret` (HTTP Basic).

## Tests

```bash
uv run pytest examples/reference-app tests/integration -q
```

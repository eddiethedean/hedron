# Hedron 0.15 data-app demo

Minimal FastAPI sample for the **0.15** train: `region` / `@fragment` / `swap`, a typed
`DateInput`, `Map` (with table alternative), Gallery/Audio stubs, and `mark=` attributes.
OIDC and connection-registry imports are commented stubs.

```bash
uv sync
uv run uvicorn app:app --app-dir examples/data-app-0.15 --reload
```

Explorer is off; replace `session_secret` before any shared deployment.

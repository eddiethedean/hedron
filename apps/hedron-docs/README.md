# hedron-docs proving app

This is the deployable ASGI entrypoint for the experimental `hedron-docs` 0.5 native-rendering
compiler slice.
It compiles the bundled fixture corpus once during application startup and serves only the immutable
manifest at request time.

```bash
uv run uvicorn --app-dir apps/hedron-docs app:app
```

FastAPI Cloud entrypoint: `apps/hedron-docs/app.py:app`.

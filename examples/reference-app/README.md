# Hedron reference application (FastAPI)

Cumulative authenticated team-administration application for the FastAPI flagship.
Tracks the **0.16.0** train (portable conformance / optional native accel on the 0.9 HDJ
authoring line).

Demonstrates:

- `Hedron()` and plain `FastAPI` + `HedronRouter` modes
- Lazy addressable `UserTable` protected by router dependencies
- Typed create/update/delete actions with CSRF validation
- HTMX fragment swaps and bundled HTMX 2.0.10
- DataEditor, Auto, cache helpers, and ColorMode
- Charts (`LineChart` via **Alpha** `hedron[charts]`), Markdown, typed `InteractionResult`,
  declared fragment regions, and `/charts/*` interaction routes
- Offline static rendering helpers
- Optional `hedron[native]` acceleration (off by default semantics; install to enable
  Rust escaping with pure-Python fallback) and `hedron conformance` kit visibility

## Run (local)

```bash
uv sync
uv run uvicorn app:app --app-dir examples/reference-app
```

Default credentials: `admin` / `secret` (HTTP Basic). **Replace before any shared or
production deploy.**

Open the home page for CRUD + DataEditor + charts/Markdown. Chart interaction endpoints
live under `/charts/*` (for example `/charts/fragment`, `/charts/search`).

## Docker

Compose under this directory is **maintainer experimental** and may require local static
assets / proxy config that are not part of the default clone. Prefer the `uvicorn`
command above for adopters. Production packaging guidance (generic Dockerfile pattern):
[Deployment](https://hedron.readthedocs.io/en/latest/guides/deployment/). If you need
containers from this tree, start from [`Dockerfile`](Dockerfile) and fix the module path
to match how you copy the app (`app:app` with `WORKDIR` set to the app directory is the
usual pattern).

## Tests

```bash
uv run pytest examples/reference-app tests/integration -q
```

Optional extras (`charts`, `markdown`, sanitizer) are part of the workspace sync; when
developing against a minimal install, add `hedron[charts]`, `hedron[markdown]`, and a
chart backend such as `hedron-charts[matplotlib]`.

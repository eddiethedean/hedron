# Try Hedron with Codespaces / Dev Container

**No local Python required** — open the repo in GitHub Codespaces or a Dev Container,
then run a real Hedron server.

!!! note "What this is not"

    There is no hosted multi-tenant sandbox and no one-liner “try Hedron” without a
    container or local install. Codespaces / Dev Container is the remote path.

## Recommended — Hello scaffold

This repository includes a [Dev Container](https://containers.dev/) definition at
[`.devcontainer/devcontainer.json`](https://github.com/eddiethedean/hedron/blob/main/.devcontainer/devcontainer.json).

1. Open the repo in GitHub Codespaces **or** VS Code / Cursor → “Reopen in Container”.
2. Wait until the container finishes `uv sync` (terminal prompt returns; `uv` is on PATH).
3. Run the Hello scaffold:

```bash
uvx --from "hedron>=0.20.0,<0.21" hedron new /tmp/my-hedron-app
cd /tmp/my-hedron-app && uv sync
uv run uvicorn app:app --host 0.0.0.0 --port 8000
```

!!! note "PyPI vs `main`"

    Until `v0.20.0` is tagged, PyPI still serves **`v0.18.0`**. The Dev Container / Codespaces
    path uses this repo’s `main` workspace, so you get Ready-to-cut `0.20.0` without waiting
    for the tag.

4. Forward port **8000** and open the URL. You should see **Hello from hedron new**.
   Click **Refresh status** — the page updates without a full reload (HTMX swaps a small
   HTML fragment into the declared region).

Hello has **no login**. Prefer this path for the first five minutes.

## More samples (stop Hello first)

Only one process can bind port **8000**. Stop the Hello server (`Ctrl+C`) before starting
another sample.

### Reference app (CRUD demo — has login)

```bash
uv run uvicorn app:app --app-dir examples/reference-app --host 0.0.0.0 --port 8000
```

!!! danger "Demo credentials are for local / Codespaces demos only"

    Reference-app login: `admin` / `secret`. **Never** deploy these credentials.
    Change them before any shared or production environment.

### Flask / Django adapter slices

```bash
# Flask
uv run python examples/flask-reference/app.py

# Django (manage-less — no manage.py)
cd examples/django-reference
uv run waitress-serve --listen=0.0.0.0:8000 wsgi:application
```

### Live interaction (polling Supported; SSE/WS experimental)

```bash
uv run uvicorn app:app --app-dir examples/live-interaction --host 0.0.0.0 --port 8000
```

## Option B — Local install (no container)

See [Build your first app](../getting-started/quickstart.md) for uv → scaffold → Hello.
That path does not require cloning this repository.

## Local after clone

Prefer Hello first (same as recommended), then optional demos:

```bash
git clone https://github.com/eddiethedean/hedron.git
cd hedron
uv sync
uvx --from "hedron>=0.20.0,<0.21" hedron new /tmp/my-hedron-app
cd /tmp/my-hedron-app && uv sync
uv run uvicorn app:app --reload
```

Next: [Quickstart](../getting-started/quickstart.md) ·
[Learning path](../getting-started/learning-path.md) ·
[Runnable examples](runnable.md).

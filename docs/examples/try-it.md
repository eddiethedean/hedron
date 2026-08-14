# Try Hedron with Codespaces / Dev Container

**Fastest path if you already have Python:** skip this page and use
[Build your first app](../getting-started/quickstart.md) (no clone required).

**No local Python install required** — open this repository in GitHub Codespaces or a Dev
Container, then run a **real** Hedron server (still not a hosted playground). Plan on
**~10+ minutes** for the first Codespaces / Dev Container boot.

!!! note "What this is not"

    There is no multi-tenant hosted sandbox and no one-liner “try Hedron” without a
    container or local install. Codespaces / Dev Container is the remote path — first
    sync often takes **5–15 minutes**.

## Why open the repo?

The Dev Container installs tooling (`uv`, Python) from this monorepo. The Hello demo below
still scaffolds a **published** `hedron` app under `/tmp` — you are not required to run
in-tree examples first. Prefer [local quickstart](../getting-started/quickstart.md) if you
already have Python and do not want to clone.

## Recommended — Hello scaffold

This repository includes a [Dev Container](https://containers.dev/) definition at
[`.devcontainer/devcontainer.json`](https://github.com/eddiethedean/hedron/blob/main/.devcontainer/devcontainer.json).

1. Open the repo in GitHub Codespaces **or** VS Code / Cursor → “Reopen in Container”.
2. Wait until the container finishes `uv sync` (terminal prompt returns; `uv` is on PATH).
   First boot often takes **5–15 minutes** because the Dev Container syncs the full
   monorepo (including the docs dependency group) — not a 60-second sandbox.
3. Run the Hello scaffold (published pin — independent of editable workspace packages):

```bash
uvx --from "hedron>=0.36.0,<0.37" hedron new /tmp/my-hedron-app
cd /tmp/my-hedron-app && uv sync
uv run uvicorn app:app --host 0.0.0.0 --port 8000
```

Pin production installs with `hedron>=0.36.0,<0.37`.

4. Forward port **8000** and open the URL. You should see **Hello from hedron new**.
   Click **Refresh status** — the page updates without a full reload (HTMX swaps a small
   HTML fragment into the declared region).

Hello has **no login**. Prefer this path for the first five minutes.

## More samples (stop Hello first)

Only one process can bind port **8000**. Stop the Hello server (`Ctrl+C`) before starting
another sample. These use the **cloned workspace** packages:

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
That path does **not** require cloning this repository.

## Local after clone

```bash
git clone https://github.com/eddiethedean/hedron.git
cd hedron
uv sync
uvx --from "hedron>=0.36.0,<0.37" hedron new /tmp/my-hedron-app
cd /tmp/my-hedron-app && uv sync
uv run uvicorn app:app --reload
```

Next: [Quickstart](../getting-started/quickstart.md) ·
[Learning path](../getting-started/learning-path.md) ·
[Runnable examples](runnable.md).

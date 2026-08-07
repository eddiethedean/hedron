# Try Hedron with Codespaces / Dev Container

**No local Python required** — open the repo in GitHub Codespaces or a Dev Container,
then run a real Hedron server.

!!! note "What this is not"

    There is no hosted multi-tenant sandbox and no one-liner “try Hedron” without a
    container or local install. Codespaces / Dev Container is the remote path.

## Option A — Codespaces / Dev Container (recommended)

This repository includes a [Dev Container](https://containers.dev/) definition at
[`.devcontainer/devcontainer.json`](https://github.com/eddiethedean/hedron/blob/main/.devcontainer/devcontainer.json).

1. Open the repo in GitHub Codespaces **or** VS Code / Cursor → “Reopen in Container”.
2. When the container finishes `uv sync`, run **either**:

**Hello scaffold (inside the container):**

```bash
uvx --from "hedron>=0.18.0" hedron new /tmp/my-hedron-app
cd /tmp/my-hedron-app && uv sync
uv run uvicorn app:app --host 0.0.0.0 --port 8000
```

Open the forwarded URL. You should see **Hello from hedron new**. Click **Refresh status**
— the timestamp should update.

**Reference app (larger CRUD demo):**

```bash
uv run uvicorn app:app --app-dir examples/reference-app --host 0.0.0.0 --port 8000
```

**Flask adapter slice:**

```bash
uv run python examples/flask-reference/app.py
# or follow examples/flask-reference/README.md
```

**Django adapter slice:**

```bash
cd examples/django-reference
uv run python manage.py runserver 0.0.0.0:8000
```

3. Forward port **8000** and open the URL.

!!! danger "Demo credentials are for local / Codespaces demos only"

    Reference-app login: `admin` / `secret`. **Never** deploy these credentials.
    Change them before any shared or production environment.

Live interaction sample (polling Supported; SSE/WS **experimental**):

```bash
uv run uvicorn app:app --app-dir examples/live-interaction --host 0.0.0.0 --port 8000
```

## Option B — Local install (if you prefer not to use a container)

See [Build your first app](../getting-started/quickstart.md) for uv step 0 → scaffold →
Hello. That path does not require cloning this repository.

## Local after clone

```bash
git clone https://github.com/eddiethedean/hedron.git
cd hedron
uv sync
uv run uvicorn app:app --app-dir examples/reference-app --reload
```

Next: [Quickstart](../getting-started/quickstart.md) ·
[Flask](../getting-started/flask.md) · [Django](../getting-started/django.md) ·
[Runnable examples](runnable.md).

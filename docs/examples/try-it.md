# Try Hedron with Codespaces / Dev Container

**Fastest path to Hello:** scaffold a tiny app (local or Codespaces), then explore larger demos.

!!! note "What this is not"

    There is no hosted multi-tenant sandbox and no one-liner “try Hedron” without a
    container or local install. Codespaces / Dev Container is the Supported remote path.

## Option A — Hello in ~5 minutes (recommended)

=== "uv (recommended)"

    ```bash
    uvx --from "hedron>=0.18.0" hedron new my-hedron-app
    cd my-hedron-app && uv sync
    uv run uvicorn app:app --reload
    ```

=== "pip (venv)"

    ```bash
    python -m venv .venv
    source .venv/bin/activate   # Windows PowerShell: .\.venv\Scripts\Activate.ps1
    python -m pip install "hedron>=0.18.0" "uvicorn[standard]"
    python -m hedron new my-hedron-app
    cd my-hedron-app && python -m pip install -e .
    uvicorn app:app --reload
    ```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000) — you should see **Hello from hedron new**.
Next: [Quickstart](../getting-started/quickstart.md) →
[HTMX interactions](../guides/htmx-interactions.md).

## Option B — Codespaces / Dev Container (full reference app)

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

**Reference app (larger CRUD demo):**

```bash
uv run uvicorn app:app --app-dir examples/reference-app --host 0.0.0.0 --port 8000
```

3. Forward port **8000** and open the URL.

!!! danger "Demo credentials are for local / Codespaces demos only"

    Reference-app login: `admin` / `secret`. **Never** deploy these credentials.
    Change them before any shared or production environment.

Live interaction sample (polling Supported; SSE/WS **experimental**):

```bash
uv run uvicorn app:app --app-dir examples/live-interaction --host 0.0.0.0 --port 8000
```

## Local after clone

```bash
git clone https://github.com/eddiethedean/hedron.git
cd hedron
uv sync
# Hello-sized: uvx --from "hedron>=0.18.0" hedron new /tmp/my-hedron-app && …
# Or the reference app:
uv run uvicorn app:app --app-dir examples/reference-app --reload
```

See [Installation](../getting-started/installation.md) and the
[quickstart](../getting-started/quickstart.md).

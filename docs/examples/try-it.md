# Try Hedron with Codespaces / Dev Container

**Fastest no-local-Python path:** open this repo in GitHub Codespaces (or a Dev Container),
run the reference app, and log in with the demo credentials below.

Prefer a machine install instead?
[Get started](../getting-started/quickstart.md) (`hedron new`) or a
[single-file app](single-file.md).

!!! note "What this is not"

    There is no hosted multi-tenant sandbox and no one-liner “try Hedron” without a
    container or local install. Codespaces / Dev Container is the Supported remote path.

## Dev Container / Codespaces

This repository includes a [Dev Container](https://containers.dev/) definition at
[`.devcontainer/devcontainer.json`](https://github.com/eddiethedean/hedron/blob/main/.devcontainer/devcontainer.json).

1. Open the repo in GitHub Codespaces **or** VS Code / Cursor → “Reopen in Container”.
2. When the container finishes `uv sync`, run:

```bash
uv run uvicorn app:app --app-dir examples/reference-app --host 0.0.0.0 --port 8000
```

3. Forward port **8000** and open the URL. Demo login: `admin` / `secret`.

Live interaction sample (polling Supported; SSE/WS **experimental**):

```bash
uv run uvicorn app:app --app-dir examples/live-interaction --host 0.0.0.0 --port 8000
```

## Local after clone

```bash
git clone https://github.com/eddiethedean/hedron.git
cd hedron
uv sync
uv run uvicorn app:app --app-dir examples/reference-app --reload
```

## Local without clone

```bash
python -m venv .venv && source .venv/bin/activate
python -m pip install "hedron>=0.17.0" "uvicorn[standard]"
python -m hedron new my-hedron-app
cd my-hedron-app
python -m pip install -e .
uvicorn app:app --reload
```

See [Installation](../getting-started/installation.md) and the
[quickstart](../getting-started/quickstart.md).

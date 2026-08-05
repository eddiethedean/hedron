# Try Hedron with Codespaces / Dev Container

There is no hosted “try it without cloning” sandbox and **no single-command try-it**.
The Supported evaluator paths are **GitHub Codespaces**, a local **Dev Container**,
[`hedron new`](../getting-started/installation.md) on your machine, or a
[single-file app](single-file.md) via `pip install`.

## Dev Container / Codespaces

This repository includes a [Dev Container](https://containers.dev/) definition at
[`.devcontainer/devcontainer.json`](https://github.com/eddiethedean/hedron/blob/main/.devcontainer/devcontainer.json).

1. Open the repo in GitHub Codespaces **or** VS Code / Cursor → “Reopen in Container”.
2. When the container finishes `uv sync`, run:

```bash
uv run uvicorn app:app --app-dir examples/reference-app --host 0.0.0.0 --port 8000
```

3. Forward port **8000** and open the URL. Demo login: `admin` / `secret`.

Live interaction sample:

```bash
uv run uvicorn app:app --app-dir examples/live-interaction --host 0.0.0.0 --port 8000
```

## Local after clone

```bash
uv sync && uv run uvicorn app:app --app-dir examples/reference-app --reload
```

## Prefer not to clone?

```bash
pip install "hedron>=0.11.0"
python -m hedron new my-hedron-app   # or: hedron new …
cd my-hedron-app && pip install -e .
uvicorn app:app --reload
```

See [Installation](../getting-started/installation.md) and the
[quickstart](../getting-started/quickstart.md).

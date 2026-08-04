# Try Hedron in one command

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

## Local one-liner (after clone)

```bash
uv sync && uv run uvicorn app:app --app-dir examples/reference-app --reload
```

No hosted “try it without cloning” sandbox is published yet—Codespaces or the Dev
Container is the Supported evaluator path.

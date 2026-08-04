# Contributing

Hedron is a Python monorepo. Full contributor documentation lives in the docs site:

- **Setup, checks, PRs:** [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md)
- **Status / freeze:** [docs/STATUS.md](docs/STATUS.md)
- **Cutting a release:** [docs/RELEASE.md](docs/RELEASE.md)

## Quick setup

**Prerequisites:** CPython **3.11–3.14** and [uv](https://docs.astral.sh/uv/).

```bash
git clone https://github.com/eddiethedean/hedron.git
cd hedron
uv sync
uv run ruff check packages tests examples
uv run pyright
uv run pytest -q
```

Docs preview: `uv sync --group docs && uv run --group docs mkdocs serve`.

Optional browser suite: install Playwright and set `HEDRON_BROWSER=1`
(see CI `browser` job). Adapter packages (`hedron-flask`, `hedron-django`) are part of
the workspace sync.

Smoke the core renderer without the FastAPI flagship:

```bash
uv run python -c "from hedron_core import Page, Text, RenderMode, render; print(render(Page(Text('Hello'), title='Hi'), mode=RenderMode.PAGE).html)"
```

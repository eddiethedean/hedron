# Contributing

Hedron is a Python monorepo. Full contributor documentation lives in the docs site:

- **Setup, checks, PRs:** [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md)
- **Code of Conduct:** [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)
- **Status / freeze:** [docs/STATUS.md](docs/STATUS.md) (canonical; root `STATUS.md` is a mirror)
- **Roadmap:** [docs/ROADMAP.md](docs/ROADMAP.md) (canonical; root `ROADMAP.md` is a mirror)
- **Cutting a release:** [docs/RELEASE.md](docs/RELEASE.md)

Edit STATUS/ROADMAP under `docs/`, then run `uv run python scripts/sync_status_roadmap.py`.

## Quick setup

**Prerequisites:** CPython **3.11–3.14** and [uv](https://docs.astral.sh/uv/).

```bash
git clone https://github.com/eddiethedean/hedron.git
cd hedron
uv sync
uv run ruff format --check packages tests examples
uv run ruff check packages tests examples
uv run pyright
uv run pytest -q
```

Docs preview: `uv sync --group docs && uv run --group docs mkdocs serve`
(or `./scripts/mkdocs.sh serve`). Strict builds: `uv run --group docs mkdocs build --strict`.

CI runs `test`, `quality`, **browser** (Chromium on PRs), and **evidence** on every
pull request — see [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md). Local Playwright is
optional for docs-only work. Adapter packages (`hedron-flask`, `hedron-django`) are part of
the workspace sync.

Smoke the core renderer without the FastAPI flagship:

```bash
uv run python -c "from hedron_core import Page, Text, RenderMode, render; print(render(Page(Text('Hello'), title='Hi'), mode=RenderMode.PAGE).html)"
```

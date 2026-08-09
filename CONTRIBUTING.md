# Contributing

Hedron is a Python monorepo. Full contributor documentation lives in the docs site:

- **Day-one (docs PR / small bug):** [docs/guides/contributor-day-one.md](docs/guides/contributor-day-one.md)
- **Documentation standards:** [docs/guides/documentation-standards.md](docs/guides/documentation-standards.md)
- **Setup, checks, PRs:** [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md)
- **Code of Conduct:** [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)
- **Status / freeze:** [docs/STATUS.md](docs/STATUS.md) (canonical; root `STATUS.md` is a mirror)
- **Roadmap:** [docs/ROADMAP.md](docs/ROADMAP.md) (canonical; root `ROADMAP.md` is a mirror)
- **Cutting a release:** [docs/RELEASE.md](docs/RELEASE.md)

Edit STATUS/ROADMAP under `docs/`, then run `uv run python scripts/sync_status_roadmap.py`
(note: syncing root mirrors is **not** docs-only CI — see
[CI path filters](docs/CONTRIBUTING.md#ci-path-filters)).

## Quick setup

**Prerequisites:** CPython **3.11–3.14** and [uv](https://docs.astral.sh/uv/).

**Docs-only first contribution** (preferred):

```bash
git clone https://github.com/eddiethedean/hedron.git
cd hedron
uv sync --group docs
uv run --group docs mkdocs build --strict
uv run python scripts/check_docs_train_ssot.py
uv run python scripts/check_recipe_code_sync.py
uv run python scripts/generate_sim_demos.py --check
```

**Code / bug fix** (full workspace):

```bash
git clone https://github.com/eddiethedean/hedron.git
cd hedron
uv sync
# Same suites as GitHub Actions (preferred):
bash scripts/ci_checks.sh test --python 3.12
bash scripts/ci_checks.sh quality --python 3.12
# Or the individual tools:
uv run ruff format --check packages tests examples
uv run ruff check packages tests examples
uv run pyright
uv run pytest -q
```

Docs preview: `uv sync --group docs && uv run --group docs mkdocs serve`
(or `./scripts/mkdocs.sh serve`). Strict builds: `uv run --group docs mkdocs build --strict`.

CI (`ci.yml`) runs `quality` on every PR; `test` / `browser` / `evidence` skip on
docs-only allowlisted PRs — see [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md).
Full `quality` installs a Rust toolchain in CI for `hedron-native` wheels; docs-only
local verify does not need Rust. Adapter packages (`hedron-flask`, `hedron-django`) are
part of the workspace sync.

Smoke the core renderer without the FastAPI flagship:

```bash
uv run python -c "from hedron_core import Page, Text, RenderMode, render; print(render(Page(Text('Hello'), title='Hi'), mode=RenderMode.PAGE).html)"
```

# Contributing

**Start here:** [Contributor day-one](docs/guides/contributor-day-one.md)
(docs typo / small bug). Full guide: [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md).

| Need | Page |
|---|---|
| First contribution | [Contributor day-one](docs/guides/contributor-day-one.md) |
| Setup, CI path filters, PRs | [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md) |
| Docs voice / Diátaxis | [Documentation standards](docs/guides/documentation-standards.md) |
| Code of Conduct | [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) |
| Status / freeze | [docs/STATUS.md](docs/STATUS.md) (root `STATUS.md` is a mirror) |
| Roadmap | [docs/ROADMAP.md](docs/ROADMAP.md) (root `ROADMAP.md` is a mirror) |
| Cutting a release | [docs/RELEASE.md](docs/RELEASE.md) |

Edit STATUS/ROADMAP under `docs/`, then run `uv run python scripts/sync_status_roadmap.py`
only when a maintainer asked — syncing root mirrors is **not** docs-only CI (see
[CI path filters](docs/CONTRIBUTING.md#ci-path-filters)).

## Docs-only (preferred first PR)

```bash
git clone https://github.com/eddiethedean/hedron.git
cd hedron
uv sync --group docs
uv run --group docs mkdocs build --strict
uv run python scripts/check_docs_train_ssot.py
uv run python scripts/check_package_docs_inventory.py
uv run python scripts/verify_pkg_38.py --allow-planned
uv run python scripts/check_recipe_code_sync.py
uv run python scripts/generate_sim_demos.py --check
```

**Local verify does not need Rust or Playwright.** GitHub Actions still runs the
**quality** job on docs-only PRs (mkdocs + SSOT checks **and** package wheel builds).
That wheel step installs a Rust toolchain **in CI** — you do not need it locally for
typos. Details: [Contributor day-one](docs/guides/contributor-day-one.md).

## Code / bug fix

```bash
git clone https://github.com/eddiethedean/hedron.git
cd hedron
uv sync
bash scripts/ci_checks.sh test --python 3.12
bash scripts/ci_checks.sh quality --python 3.12
```

Docs preview: `uv sync --group docs && uv run --group docs mkdocs serve`
(or `./scripts/mkdocs.sh serve`).

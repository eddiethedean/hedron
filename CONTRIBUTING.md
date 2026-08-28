# Contributing

**Start here:** [Contributor day-one](docs/guides/contributor-day-one.md)
(docs typo / small bug). Full guide: [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md).

| Need | Page |
|---|---|
| First contribution | [Contributor day-one](docs/guides/contributor-day-one.md) |
| Setup, CI path filters, PRs | [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md) |
| Docs voice / Diátaxis | [Documentation standards](docs/guides/documentation-standards.md) |
| Release facts, generated indexes, and archives | [Documentation contribution guide](docs/guides/documentation-contributing.md) |
| Code of Conduct | [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) |
| Readiness (adopters) | [What’s ready](docs/guides/whats-ready.md) · [What’s next](docs/guides/whats-next.md) |
| Status / freeze (maintainers) | [docs/STATUS.md](docs/STATUS.md) — gate ledger, not getting-started |
| Roadmap (maintainer ledger) | [docs/ROADMAP.md](docs/ROADMAP.md) |
| Cutting a release | [docs/RELEASE.md](docs/RELEASE.md) |

Edit `docs/STATUS.md` / `docs/ROADMAP.md`. Sync STATUS with `uv run python scripts/sync_status_roadmap.py`
only when a maintainer asked — syncing root mirrors is **not** docs-only CI (see
[CI path filters](docs/CONTRIBUTING.md#ci-path-filters)).

## Docs-only (preferred first PR)

**Minimal verify** (open the PR with this):

```bash
git clone https://github.com/eddiethedean/hedron.git
cd hedron
uv sync --group docs
uv run --group docs mkdocs build --strict
uv run python scripts/check_docs_train_ssot.py
```

**Full docs wall** (before maintainers merge / when CI fails): see
[Contributor day-one](docs/guides/contributor-day-one.md).

**Local verify does not need Rust or Playwright.** Docs-only PRs run the **`docs`**
CI suite (mkdocs + SSOT + recipe/sim checks) and **skip** the Rust toolchain and
package wheel builds. Packet scripts (`verify_pkg_*`) belong on full `quality` runs —
see [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md). Default `pytest` uses xdist `-n auto`;
browser tests need `HEDRON_BROWSER=1 uv run pytest -q -m browser -n 0`. Details:
[Contributor day-one](docs/guides/contributor-day-one.md).
## Code / bug fix

```bash
git clone https://github.com/eddiethedean/hedron.git
cd hedron
uv sync
bash scripts/ci_checks.sh test --python 3.12
bash scripts/ci_checks.sh quality --python 3.12
# Full CI parity (long; skip browser locally if Playwright is not installed):
# bash scripts/ci_checks.sh all --python 3.12 --skip-browser
```

Docs preview: `uv sync --group docs && uv run --group docs mkdocs serve`
(or `./scripts/mkdocs.sh serve`).

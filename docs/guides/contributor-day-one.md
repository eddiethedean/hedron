# Contributor day-one

**Canonical first-contribution page.** The repository root `CONTRIBUTING.md` stub
points here. Full detail: [Contributing](../CONTRIBUTING.md).

## Docs-only PR

**Local work (~15 minutes):** edit markdown and build docs — **no Rust, no Playwright**.

```bash
git clone https://github.com/eddiethedean/hedron.git
cd hedron
uv sync --group docs
uv run --group docs mkdocs build --strict
uv run python scripts/check_docs_train_ssot.py
uv run python scripts/check_package_docs_inventory.py
uv run python scripts/check_documentation_ownership.py
uv run python scripts/check_api_docs_coverage.py
uv run python scripts/check_package_readme_links.py
uv run python scripts/check_recipe_code_sync.py
uv run python scripts/generate_component_docs.py --check
uv run python scripts/generate_sim_demos.py --check
```

If you edit generated component pages, also run
`uv run python scripts/generate_component_docs.py` (then commit the regenerated files).

Docs-only PRs (allowlisted paths) run the **`docs`** CI suite: mkdocs, train SSOT, and
recipe/sim checks. They **do not** install a Rust toolchain or run `uv build --all-packages`.
Allowlist: [CI path filters](../CONTRIBUTING.md#ci-path-filters).

If your PR also changes `packages/`, `examples/`, `tests/`, root `STATUS.md`,
`scripts/sync_status_roadmap.py`, or CI itself, the **full** matrix runs.

Open a PR with **“docs-only”** in the title or first line of the description.

This repository has no `.pre-commit-config.yaml` — ignore generic `--no-verify` advice
from other projects.

### STATUS sync

Canonical STATUS lives under `docs/STATUS.md`; root `STATUS.md` is a generated mirror.
The roadmap is only `docs/ROADMAP.md`. Leave the root STATUS mirror untouched unless a
maintainer asked for a STATUS sync.

## Good first issues

Browse GitHub issues labeled
[`good first issue`](https://github.com/eddiethedean/hedron/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22)
when the queue has open items. **If the label is empty**, prefer:

- Typos, dead links, and Install/FAQ/Troubleshooting clarity
- Example README fixes that match the living `0.52` train pins
- Small test coverage for an existing bug you hit

Avoid starting with release-gate TOMLs, STATUS ledgers, or phase packets unless a
maintainer asked you to.

## Bug-fix and package PRs

Use the full [Contributing](../CONTRIBUTING.md) guide: `uv sync --all-groups`,
`verify_pkg_*`, and `bash scripts/ci_checks.sh quality --python 3.12` (Rust may be
required for native wheel smoke).

## Plugins and RFCs (second contribution)

- Plugin sample / authoring: [Plugin authoring](plugin-authoring.md) ·
  [Using plugins](plugin-consumer.md) (`hedron-sample-kit>=0.1.10,<0.2` on 0.51).
- Public contract changes: [Changing public contracts](../CONTRIBUTING.md#changing-public-contracts)
  (RFC intake steps).

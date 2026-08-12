# Contributor day-one

**Canonical first-contribution page.** The repository root `CONTRIBUTING.md` stub
points here. Full detail: [Contributing](../CONTRIBUTING.md).

## Docs-only PR

**Local work (~15 minutes):** edit markdown and build docs — **no Rust, no Playwright**.

**CI (important):** PRs that touch only allowlisted docs paths skip `test` / `browser` /
`evidence` / packaging rehearsal, but **still run `quality`**. That job includes mkdocs +
train SSOT + recipe/sim checks **and package wheel builds** (CI installs a Rust toolchain
for `hedron-native`). A docs typo PR therefore waits on wheels in GitHub Actions even when
your laptop never builds them. Allowlist:
[CI path filters](../CONTRIBUTING.md#ci-path-filters).

If your PR also changes `packages/`, `examples/`, `tests/`, root `STATUS.md` /
`ROADMAP.md`, `scripts/sync_status_roadmap.py`, or CI itself, the **full** matrix runs.

1. Clone and sync docs deps:

   ```bash
   git clone https://github.com/eddiethedean/hedron.git
   cd hedron
   uv sync --group docs
   ```

2. Edit markdown under `docs/` (or root README stubs that point at docs).

3. Verify locally (matches the docs portion of `quality`):

   ```bash
   uv run --group docs mkdocs build --strict
   uv run python scripts/check_docs_train_ssot.py
   uv run python scripts/check_recipe_code_sync.py
   uv run python scripts/generate_sim_demos.py --check
   ```

   If you edit generated component pages, also run
   `uv run python scripts/generate_component_docs.py` (then commit the regenerated files).

4. Open a PR with **“docs-only”** in the title or first line of the description.

This repository has no `.pre-commit-config.yaml` — ignore generic `--no-verify` advice
from other projects.

For quality-suite work beyond docs, use `uv sync --all-groups` (and install a
[Rust toolchain](https://rustup.rs/) if `hedron-native` wheel builds fail) before
`bash scripts/ci_checks.sh quality --python 3.12`.

### STATUS / ROADMAP footgun

Canonical STATUS/ROADMAP live under `docs/`. Root `STATUS.md` / `ROADMAP.md` are
generated mirrors. Running `uv run python scripts/sync_status_roadmap.py` updates the
root mirrors, which are **not** on the docs-only allowlist — that PR will run full CI.
Prefer docs-only edits that leave root mirrors untouched unless a maintainer asked for a
STATUS sync.

## Good first issues

Browse GitHub issues labeled
[`good first issue`](https://github.com/eddiethedean/hedron/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22)
when the queue has open items. **If the label is empty**, prefer docs clarity,
FAQ/Troubleshooting, or a small failing test for a bug you hit — see below. Do not wait
for a labeled issue to open a small PR.

## Bug-fix PR

1. `uv sync` then reproduce with `uv run pytest -q` (narrow to the failing file when
   possible).
2. Prefer a failing test first, then the fix.
3. Run `bash scripts/ci_checks.sh test --python 3.12` and
   `bash scripts/ci_checks.sh quality --python 3.12` before pushing when you can
   (Rust may be required for native wheel smoke in `quality`).

Skip RFC / decision vocabulary unless your change alters a public contract — see
[Bugs vs RFCs vs decisions](../CONTRIBUTING.md#bugs-vs-rfcs-vs-decisions) in the full guide.

## Good first contributions

- Typos, dead links, and Install/FAQ/Troubleshooting clarity
- Example README fixes that match the living `0.29` train pins
- Small test coverage for an existing bug you hit

Avoid starting with release-gate TOMLs, STATUS ledgers, or phase packets unless a
maintainer asked you to.

## Plugins and RFCs (second contribution)

- Plugin sample / authoring: [Plugin authoring](plugin-authoring.md) ·
  [Using plugins](plugin-consumer.md) (`hedron-sample-kit>=0.1.10,<0.2` on 0.28).
- Public contract changes: [Changing public contracts](../CONTRIBUTING.md#changing-public-contracts)
  (RFC intake steps).

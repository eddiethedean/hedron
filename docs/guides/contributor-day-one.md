# Contributor day-one

Thin on-ramp for first contributions. Full detail:
[Contributing](../CONTRIBUTING.md).

## Docs-only PR

**Local work (~15 minutes):** edit markdown and build docs. **CI:** PRs that touch only
docs paths (`docs/**`, root README/SECURITY stubs, `mkdocs.yml`, and the docs sync/generate
scripts listed in `.github/workflows/ci.yml`) skip `test` / `browser` / `evidence` /
packaging rehearsal and still run **quality** (mkdocs + train SSOT + package checks).
If your PR also changes `packages/`, `examples/`, `tests/`, or CI itself, the full matrix
runs.

1. Clone and sync docs deps:

   ```bash
   git clone https://github.com/eddiethedean/hedron.git
   cd hedron
   uv sync --group docs
   ```

2. Edit markdown under `docs/` (or root README stubs that point at docs).

3. Verify locally:

   ```bash
   uv run --group docs mkdocs build --strict
   python scripts/check_docs_train_ssot.py
   ```

4. Open a PR with **“docs-only”** in the title or first line of the description.

You do **not** need Playwright, RFCs, or acceptance gates locally for typos and guide
fixes. Do not use `--no-verify`. For quality-suite work beyond docs, use
`uv sync --all-groups` before `bash scripts/ci_checks.sh quality --python 3.12`.

## Good first issues

Browse GitHub issues labeled
[`good first issue`](https://github.com/eddiethedean/hedron/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22)
when present. If the label is empty, prefer docs clarity, FAQ/Troubleshooting, or a small
failing test for a bug you hit — see below.

## Bug-fix PR

1. `uv sync` then reproduce with `uv run pytest -q` (narrow to the failing file when
   possible).
2. Prefer a failing test first, then the fix.
3. Run `bash scripts/ci_checks.sh test --python 3.12` and
   `bash scripts/ci_checks.sh quality --python 3.12` before pushing when you can.

Skip RFC / decision vocabulary unless your change alters a public contract — see
[Bugs vs RFCs vs decisions](../CONTRIBUTING.md#bugs-vs-rfcs-vs-decisions) in the full guide.

## Good first contributions

- Typos, dead links, and Install/FAQ/Troubleshooting clarity
- Example README fixes that match the living `0.25` train pins
- Small test coverage for an existing bug you hit

Avoid starting with release-gate TOMLs, STATUS ledgers, or phase packets unless a
maintainer asked you to.

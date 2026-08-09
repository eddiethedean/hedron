# Contributor day-one

Thin on-ramp for first contributions. Full detail:
[Contributing](../CONTRIBUTING.md).

## Docs-only PR (about 15 minutes)

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

You do **not** need Playwright, RFCs, or acceptance gates for typos and guide fixes.

### CI note

GitHub Actions still runs `test`, `quality`, `browser`, and `evidence` on every PR (no
path filters today). If `browser` or `evidence` fails for reasons **unrelated** to your
markdown change, ask a maintainer to re-run or waive — do not expand the diff to chase
unrelated flakes, and do not use `--no-verify`.

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
- Example README fixes that match the living `0.24` train pins
- Small test coverage for an existing bug you hit

Avoid starting with release-gate TOMLs, STATUS ledgers, or phase packets unless a
maintainer asked you to.

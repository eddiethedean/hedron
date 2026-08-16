# Contributing

## First contribution

**New here?** Start with the thin on-ramp:
[Contributor day-one](guides/contributor-day-one.md) (local docs verify ~15 minutes;
**canonical first-contribution page** — root `CONTRIBUTING.md` points there).

Docs-only PRs still run the **`quality`** job (including **package wheel builds** —
Rust toolchain in CI, not required on your laptop for typos). `test` / `browser` /
`evidence` skip when every changed path is allowlisted (see
[CI path filters](#ci-path-filters) below). The rest of this page is the full contributor
guide.

**Prerequisites:** CPython **3.11–3.14** and [uv](https://docs.astral.sh/uv/).

| OS | Notes |
|---|---|
| macOS / Linux | Primary CI agents; use the commands below as-is |
| Windows | Supported for unit/integration via the same `uv` workflow; prefer PowerShell or Git Bash. Playwright browser job is Linux CI — run Chromium locally only if you change browser tests |

**Expected local times (approximate, warm cache):**

| Suite | Typical time |
|---|---|
| `ruff` format + check | < 1 min |
| `pyright` | 1–3 min |
| `pytest -q` (default, xdist `-n auto`, no browser) | 2–5 min |
| `mkdocs build --strict` | 1–2 min |
| Playwright Chromium (`HEDRON_BROWSER=1`) | 5–15+ min |

```bash
git clone https://github.com/eddiethedean/hedron.git
cd hedron
uv sync
# Preferred: same suites as GitHub Actions (scripts/ci_checks.sh)
bash scripts/ci_checks.sh test --python 3.12
bash scripts/ci_checks.sh quality --python 3.12
# Or the individual tools:
uv run ruff format --check packages tests examples
uv run ruff check packages tests examples
uv run pyright
uv run pytest -q
```

**Docs-only changes (local verify):**

Writing, source-ownership, generated-content, and review conventions:
[Documentation standards](guides/documentation-standards.md).

```bash
uv sync --group docs
uv run --group docs mkdocs build --strict
# or preview: uv run --group docs mkdocs serve
# or: ./scripts/mkdocs.sh serve
uv run python scripts/check_docs_train_ssot.py
uv run python scripts/check_package_docs_inventory.py
uv run python scripts/verify_pkg_39.py --allow-planned
uv run python scripts/check_documentation_ownership.py
uv run python scripts/check_api_docs_coverage.py
uv run python scripts/check_package_readme_links.py
uv run python scripts/check_recipe_code_sync.py
uv run python scripts/generate_component_docs.py --check
uv run python scripts/generate_sim_demos.py --check
# quality suite also covers docs checks after `uv sync --all-groups`:
# bash scripts/ci_checks.sh quality --python 3.12
```

You do **not** need Playwright or the full pytest suite locally for markdown/typo PRs.

### CI path filters

Docs-only PRs (allowlisted paths in `.github/workflows/ci.yml`) still run **`quality`**
(lint, types, wheels, docs strict, train SSOT, recipe/sim checks) but **skip** `test`,
`browser`, and `evidence`. Allowlisted paths today:

- `docs/*`, `README.md`, `CONTRIBUTING.md`, `SECURITY.md`, `CODE_OF_CONDUCT.md`, `mkdocs.yml`
- `scripts/sync_demo_code_tabs.py`, `scripts/generate_component_docs.py`,
  `scripts/generate_sim_demos.py`, `scripts/check_docs_train_ssot.py`,
  `scripts/check_package_docs_inventory.py`,
  `scripts/check_documentation_ownership.py`, `scripts/check_api_docs_coverage.py`,
  `scripts/check_package_readme_links.py`, `scripts/check_external_links.py`,
  `scripts/check_recipe_code_sync.py`, `scripts/README.md`

**Not docs-only** (triggers the full matrix): root `STATUS.md` mirror,
`scripts/sync_status_roadmap.py`, package/source changes, or any other non-allowlisted path.
Edit `docs/STATUS.md` / `docs/ROADMAP.md`. Sync STATUS with `uv run python scripts/sync_status_roadmap.py`
only when you intend a full CI run.

Contributors should:

1. Run the local docs verify commands above (including train SSOT, recipe sync, and
   `generate_sim_demos.py --check` when you touch demos/recipes).
2. Open the PR with a clear “docs-only” note in the description when the diff stays on
   the allowlist.
3. If a non-docs job fails for reasons **unrelated** to your change, ask a maintainer to
   re-run or waive — **do not** expand the diff to chase unrelated flakes.

**Hooks:** this repository does not ship a `.pre-commit-config.yaml`; ignore generic
`--no-verify` advice from other projects.
When to leave Read the Docs for the GitHub corpus: RFCs, acceptance gates, STATUS/ROADMAP
internals, ENGINEERING_BASELINE, and DECISIONS are **excluded from the public MkDocs site**
— edit them on GitHub; adopters should stay on What’s ready / guides / API pages.
Foundations non-goals and performance budgets **are** published on RTD under
**Evaluate** / **Project → Maintainers** (not the adopter golden path).

**Local browser suite (optional):** install Playwright Chromium, then:

```bash
uv run playwright install chromium
HEDRON_BROWSER=1 uv run pytest -q -m browser -n 0
```

Smoke the core renderer without the FastAPI flagship:

```bash
uv run python -c "from hedron_core import Page, Text, RenderMode, render; print(render(Page(Text('Hello'), title='Hi'), mode=RenderMode.PAGE).html)"
```

### Which tests to run

| Change area | Suggested command |
|---|---|
| Single package / unit | `uv run pytest tests/unit -q` (or path to the test file) |
| FastAPI integration | `uv run pytest tests/integration -q` |
| Adapters | `uv run pytest tests/adapters -q` |
| Security corpus | `uv run pytest tests/security -q` |
| Conformance | `uv run pytest tests/conformance -q` |
| Examples | `uv run pytest examples -q` |
| Full default suite | `uv run pytest -q` |

Prefer the narrowest suite that covers your change before opening a PR.

### Good first contributions

- Docs clarity / typos / broken links (no RFC)
- Example README fixes and runnable-command corrections
- Tests that close an existing issue without changing public contracts

Issue labels and bite-sized tasks vary; prefer small PRs over RFC-scale first patches.

## PR workflow

1. Fork (or branch from `main`), keep the diff focused.
2. Run the narrowest tests above locally, then `ruff` + `pyright` on touched packages.
3. Open a PR against `main`. Draft PRs are fine while CI is red; mark ready when green.
4. Expect the CI jobs below. Fix failures before asking for review.

### CI map (`.github/workflows/ci.yml` + `release.yml`)

Check **commands** live in [`scripts/ci_checks.sh`](https://github.com/eddiethedean/hedron/blob/main/scripts/ci_checks.sh).
Both commit CI and release CI call the same suites after checkout / sync / tool setup.

| Job | Suite (`ci_checks.sh …`) | On pull requests? |
|---|---|---|
| `test` | `test` — `pytest -n auto` on Python 3.11–3.14 | Yes, unless **docs-only** |
| `workbench-dependencies` | `workbench` — Workbench contract tests at minimum/latest Starlette/Uvicorn bounds | Yes, unless **docs-only** |
| `quality` | `quality` — ruff format/check, pyright, wheel build + smoke, STATUS mirror `--check` (forbids extra roadmap files), docs train SSOT, recipe/sim checks, historical 0.36–0.38 packet shape, living `verify_pkg_39.py` cut, relative doc links, `mkdocs build --strict` | **Always** |
| `browser` | `browser` — Playwright HTMX suite (`HEDRON_BROWSER=1`) — **Chromium only on PRs**; Chromium+Firefox+WebKit on `main` / `workflow_dispatch` / release | Yes, unless **docs-only** |
| `realwb` | `realwb` — REALWB-030 Docker smoke (skips when `PWB_LICENSE` unset) | Yes, unless **docs-only** or fork PR |
| `realconnect` | `realconnect` — REALCONNECT-033 Docker smoke (skips when `CONNECT_LICENSE` unset) | Yes, unless **docs-only** or fork PR |
| `evidence` | `evidence` — Evidence bundle, dependency audit, configured release gate, historical `verify_pkg_*`, and living `verify_pkg_39.py` | Yes, unless **docs-only**; also on release |
| `release` (commit CI) | `packaging` — Packaging rehearsal plus living `verify_pkg_39.py` cut | After `evidence` succeeds (skipped when docs-only) |

Local full parity: `bash scripts/ci_checks.sh all --python 3.12 --skip-browser` runs every
non-browser job on one Python; omit `--python` for the full 3.11–3.14 test matrix. Pass
`--all-browsers` to match the `main`-branch browser matrix. See `scripts/ci_checks.sh --help`.

Release workflow (`release.yml`) runs the same `test` / `quality` / `browser` / `evidence`
suites before `publish` (tag pushes only).

Local Playwright is still optional for docs-only work. On docs-only PRs, CI skips
`browser` / `evidence` / `test`; `quality` remains required (see [CI path filters](#ci-path-filters)).

**Rust:** the `quality` and `test` jobs install a Rust toolchain so `hedron-native` wheels
can build. Docs-only contributors do not need Rust locally for markdown verify; full
`bash scripts/ci_checks.sh quality` on a cold machine may require Rust if the native
package builds.

### Bugs vs RFCs vs decisions

| Change | Path |
|---|---|
| Typo, docs clarity, test-only, internal refactor | PR only — no RFC |
| Bug fix with no public contract change | Issue (optional) + PR |
| New/changed public API, security default, or Supported claim | RFC + decision update — see [Changing public contracts](#changing-public-contracts) |
| Release cut / version bump | Maintainers only — [RELEASE](https://github.com/eddiethedean/hedron/blob/main/docs/RELEASE.md) |

### PR checklist

- [ ] Focused diff; no unrelated refactors
- [ ] Tests added/updated for behavior changes
- [ ] `ruff` + `pyright` clean on touched packages
- [ ] Docs/examples updated when public behavior changes
- [ ] No coordinated version bumps unless this is a release cut
- [ ] Follow the [Code of Conduct](https://github.com/eddiethedean/hedron/blob/main/CODE_OF_CONDUCT.md)

### Packages layout

| Path | Role |
|---|---|
| `packages/hedron-core` | Framework-neutral rendering core |
| `packages/hedron` | FastAPI flagship |
| `packages/hedron-explorer` | Dev Explorer (`hedron[dev]`) |
| `packages/hedron-data` | DataTable / DataEditor (`hedron[data]`) |
| `packages/hedron-charts` | Visualization adapters (`hedron[charts]`, Beta) |
| `packages/hedron-sample-kit` | Sample plugin (Beta tooling-grade) |
| `packages/hedron-flask` | Flask adapter |
| `packages/hedron-django` | Django adapter |
| `packages/hedron-jinja` | Optional HDJ templates |
| `packages/hedron-conformance` | Language-neutral conformance kit |
| `packages/hedron-extras` | Curated extras / workbenches (`hedron[extras]`) |
| `packages/hedron-native` | Optional Rust HTML-escape acceleration (Beta) |
| `packages/hedron-notebook` | Localhost server-side notebook preview (Beta tooling-grade) |
| `packages/hedron-mcp` | Deny-by-default MCP projection (Beta) |
| `packages/hedron-gradio` | Allowlisted Gradio client interoperability (Beta) |
| `packages/hedron-sim` | Offline HTMX documentation simulator (Beta tooling-grade) |
| `packages/hedron-workbench` | Posit Workbench compatibility adapter (Beta) |
| `packages/hedron-posit` | Unified Posit Workbench / Connect adapter (Beta) |
| `packages/hedron-elements` | Web Component ABI incubator (Alpha) |
| `packages/fastapi-workbench` | Independent plain-FastAPI Workbench adapter (`1.x`) |
| `tests/` | Unit, integration, conformance, adapters, security, browser |
| `examples/reference-app` | FastAPI cumulative example |
| `examples/notes-sqlalchemy` | SQLAlchemy notes recipe |
| `examples/session-auth` | Session login recipe |
| `examples/file-upload` | Multipart upload recipe |
| `examples/live-interaction` | Poll + stream + SSE / Job SSE / WS / preload sample |
| `examples/flask-reference` | Flask slice |
| `examples/django-reference` | Django slice |
| `examples/hdj-progressive` | Optional HDJ progressive samples |
| `scripts/` | Tooling index: [`scripts/README.md`](https://github.com/eddiethedean/hedron/blob/main/scripts/README.md) |

Layout contract (GitHub): [`PROJECT_LAYOUT.md`](https://github.com/eddiethedean/hedron/blob/main/docs/PROJECT_LAYOUT.md).
CI/toolchain contract: [`ENGINEERING_BASELINE.md`](https://github.com/eddiethedean/hedron/blob/main/docs/ENGINEERING_BASELINE.md).

### Canonical doc files

| Topic | Edit here | Notes |
|---|---|---|
| STATUS / ROADMAP | `docs/STATUS.md`, `docs/ROADMAP.md` (roadmap has no generated copies) | STATUS: `uv run python scripts/sync_status_roadmap.py` (CI `--check`) |
| Adopter maturity | `docs/guides/whats-ready.md` | Public SSOT — do not send adopters to STATUS |
| Documentation conventions | `docs/guides/documentation-standards.md` | Audience, source ownership, generation, review checklist |
| Contributing | `docs/CONTRIBUTING.md` | Root `CONTRIBUTING.md` is a stub pointer |
| Security policy | `docs/SECURITY.md` | Root `SECURITY.md` is a short pointer |
| Code of Conduct | root `CODE_OF_CONDUCT.md` | `docs/CODE_OF_CONDUCT.md` points at root + reporting rules |

---

## Changing public contracts

### Before implementation

Identify the owning foundation and RFC. If behavior is absent or contradictory, update
the specification before code. Public behavior additionally requires an API contract; a
subsystem requires an implementation specification and acceptance coverage.

### RFC intake (short)

1. Skim [docs/rfcs/README.md](https://github.com/eddiethedean/hedron/blob/main/docs/rfcs/README.md)
   and pick the next free RFC number.
2. Copy [TEMPLATE.md](https://github.com/eddiethedean/hedron/blob/main/docs/rfcs/TEMPLATE.md)
   into `docs/rfcs/RFC-00NN-….md` and open a **Draft** PR early for feedback.
3. Discuss alternatives and open questions in the PR; maintainers may request a
   decision entry in `docs/DECISIONS.md` before Accept.
4. Accepted RFCs change public behavior only through an explicit decision + RFC revision
   (or a superseding RFC). Timeline is not calendar-guaranteed on the `0.x` train.

### RFC changes

Material proposals use the [RFC template](https://github.com/eddiethedean/hedron/blob/main/docs/rfcs/TEMPLATE.md). Discuss alternatives and
include security, accessibility, performance, testing, compatibility, migration, and open
questions. Accepted behavior is changed through an explicit decision entry and RFC
revision or superseding RFC.

Plugin authors: start from [Plugin authoring](guides/plugin-authoring.md) and the
sample kit (`hedron-sample-kit>=0.1.10,<0.2` on Hedron 0.30).

### Implementation changes

An implementation change must state:

- owning RFC and decision identifiers;
- public API affected;
- implementation specification section;
- acceptance scenarios added or updated;
- compatibility and migration effect;
- new dependencies, assets, or plugin capabilities.

Do not expose private helpers merely to avoid designing a stable contract. Do not add a
dependency to core when an optional adapter is sufficient. Do not introduce inferred
authorization, persistence, or trust.

### Documentation definition of done

Examples compile, links resolve, names match public typing, errors and escape hatches are
documented, and status/index tables are updated. Hosted documentation is built with MkDocs
(Material) via Read the Docs (`.readthedocs.yaml`, `mkdocs.yml`). Public `__all__` map:
[api/COVERAGE.md](api/COVERAGE.md).

Release cutting is documented in [RELEASE](https://github.com/eddiethedean/hedron/blob/main/docs/RELEASE.md). Phase evidence lives in
[STATUS](https://github.com/eddiethedean/hedron/blob/main/docs/STATUS.md) (GitHub-only).

---

## Built-in component docs (definition of done)

Every public built-in component must have a dedicated page under `docs/components/` in
the same pull request that adds the component. The generated pages are backed by the
reviewable manifest in `scripts/generate_component_docs.py`.

For a new component:

1. Implement and publicly export the component. Decide which existing component group
   owns it; add a new group only when the component has a genuinely different role.
2. Add one `ComponentDoc` entry to `COMPONENTS` in
   `scripts/generate_component_docs.py`. Document the actual public signature, every
   meaningful parameter, when to use it, what HTML or browser behavior it produces,
   its accessibility contract, and its most likely misuse. Examples must use public
   imports and safe values.
3. Give the component a useful preview in `demo_html()` or `static_demo()`.
4. If the component normally needs HTMX or a server response, set its `server` field and
   add a narrowly scoped handler in `docs/javascript/component-demos.js`.
5. Add only reusable visual rules to `docs/stylesheets/component-demos.css`.
6. Run the generator and docs checks:

   ```bash
   uv run python scripts/generate_component_docs.py
   uv run python scripts/generate_component_docs.py --check
   uv run --group docs mkdocs build --strict
   ```

7. Add a composition test, not only an isolated render assertion.

Edit the manifest and regenerate rather than editing a generated component page directly.

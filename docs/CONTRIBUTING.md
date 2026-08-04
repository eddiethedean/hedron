# Contributing

## First contribution

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

**Docs-only changes:** `uv sync --group docs && uv run --group docs mkdocs serve`
(or `./scripts/mkdocs.sh serve`). Strict builds: `uv run --group docs mkdocs build --strict`.
You do not need Playwright or the full browser suite for markdown/typo PRs.

**Optional browser suite:** install Playwright Chromium, then:

```bash
uv run playwright install chromium
HEDRON_BROWSER=1 uv run pytest tests/browser -q
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

## PR workflow

1. Fork (or branch from `main`), keep the diff focused.
2. Run the narrowest tests above locally, then `ruff` + `pyright` on touched packages.
3. Open a PR against `main`. Draft PRs are fine while CI is red; mark ready when green.
4. Expect the CI jobs below. Fix failures before asking for review.

### CI map (`.github/workflows/ci.yml`)

| Job | What it runs | Required for most PRs? |
|---|---|---|
| `test` | `pytest` on Python 3.11–3.14 | Yes |
| `quality` | ruff format/check, pyright, wheel build + smoke, STATUS/ROADMAP mirror `--check`, relative doc links, `mkdocs build --strict` | Yes |
| `browser` | Playwright HTMX suite (`HEDRON_BROWSER=1`) — **Chromium only on PRs**; Chromium+Firefox+WebKit on `main` / dispatch | Only when you change browser markup/assets/HTMX behavior |
| `evidence` | Supply-chain evidence bundle scripts | Release cuts / maintainer pushes |

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
| `packages/hedron-charts` | Visualization adapters (`hedron[charts]`) |
| `packages/hedron-sample-kit` | Sample plugin |
| `packages/hedron-flask` | Flask adapter |
| `packages/hedron-django` | Django adapter |
| `packages/hedron-jinja` | Optional HDJ templates |
| `tests/` | Unit, integration, conformance, adapters, security, browser |
| `examples/reference-app` | FastAPI cumulative example |
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
| STATUS / ROADMAP | `docs/STATUS.md`, `docs/ROADMAP.md` | Then `uv run python scripts/sync_status_roadmap.py` (CI `--check`) |
| Adopter maturity | `docs/guides/whats-ready.md` | Public SSOT — do not send adopters to STATUS |
| Contributing | `docs/CONTRIBUTING.md` | Root `CONTRIBUTING.md` is a stub pointer |
| Security policy | `docs/SECURITY.md` | Root `SECURITY.md` is a short pointer |
| Code of Conduct | root `CODE_OF_CONDUCT.md` | `docs/CODE_OF_CONDUCT.md` points at root + reporting rules |

---

## Changing public contracts

### Before implementation

Identify the owning foundation and RFC. If behavior is absent or contradictory, update
the specification before code. Public behavior additionally requires an API contract; a
subsystem requires an implementation specification and acceptance coverage.

### RFC changes

Material proposals use the [RFC template](https://github.com/eddiethedean/hedron/blob/main/docs/rfcs/TEMPLATE.md). Discuss alternatives and
include security, accessibility, performance, testing, compatibility, migration, and open
questions. Accepted behavior is changed through an explicit decision entry and RFC
revision or superseding RFC.

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

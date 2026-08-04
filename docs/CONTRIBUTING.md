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

Docs preview: `uv sync --group docs && uv run --group docs mkdocs serve`
(or `./scripts/mkdocs.sh serve`). Strict builds: `uv run --group docs mkdocs build --strict`.

Optional browser suite: install Playwright and set `HEDRON_BROWSER=1` (see CI `browser` job).

Smoke the core renderer without the FastAPI flagship:

```bash
uv run python -c "from hedron_core import Page, Text, RenderMode, render; print(render(Page(Text('Hello'), title='Hi'), mode=RenderMode.PAGE).html)"
```

### Small PRs

- Keep changes focused; prefer small reviewable PRs (docs typos, tests, narrow bug fixes).
- Add or update tests with behavior changes.
- Do not bump coordinated package versions unless the change is a release cut.
- Follow the [Code of Conduct](CODE_OF_CONDUCT.md).

You do **not** need an RFC for typo fixes, test-only changes, or internal refactors that
do not change public contracts. Jump to [Changing public contracts](#changing-public-contracts)
only when you alter shipped APIs, security behavior, or acceptance evidence.

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
| `tests/` | Unit, integration, conformance, adapters |
| `examples/reference-app` | FastAPI cumulative example |
| `examples/live-interaction` | Poll + stream sample |
| `examples/flask-reference` | Flask slice |
| `examples/django-reference` | Django slice |

Canonical **STATUS** and **ROADMAP** for the published site live under `docs/`. Keep the
root copies in sync when you edit either (`scripts/sync_status_roadmap.py`).

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

---

## Changing public contracts

### Before implementation

Identify the owning foundation and RFC. If behavior is absent or contradictory, update
the specification before code. Public behavior additionally requires an API contract; a
subsystem requires an implementation specification and acceptance coverage.

### RFC changes

Material proposals use the [RFC template](rfcs/TEMPLATE.md). Discuss alternatives and
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
(Material) via Read the Docs (`.readthedocs.yaml`, `mkdocs.yml`).

Release cutting is documented in [RELEASE](RELEASE.md). Project status lives in
[STATUS](STATUS.md).

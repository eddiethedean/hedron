# Contributing

## Contribute code

### Setup

**Prerequisites:** CPython **3.11–3.14** and [uv](https://docs.astral.sh/uv/).

```bash
git clone https://github.com/eddiethedean/hedron.git
cd hedron
uv sync
```

Workspace packages: `hedron-core`, `hedron`, `hedron-explorer`, `hedron-data`,
`hedron-charts`, `hedron-sample-kit`, `hedron-flask`, `hedron-django`.

`uv sync` (dev group) already pulls chart/content test dependencies used by the
workspace. Against a minimal consumer install, optional extras are
`hedron[charts]`, `hedron[markdown]`, `hedron[sanitize]`, and backends such as
`hedron-charts[matplotlib]`.

### Checks

```bash
uv run ruff format --check packages tests examples
uv run ruff check packages tests examples
uv run pyright
uv run pytest -q
```

### Add or change a built-in component demo

Every public built-in component must have a dedicated page under `docs/components/` in
the same pull request that adds the component. The page is part of the component's
definition of done, not a follow-up documentation task. The generated pages are backed
by the reviewable manifest in `scripts/generate_component_docs.py`.

For a new component:

1. Implement and publicly export the component. Decide which existing component group
   owns it; add a new group only when the component has a genuinely different role.
2. Add one `ComponentDoc` entry to `COMPONENTS` in
   `scripts/generate_component_docs.py`. Document the actual public signature, every
   meaningful parameter, when to use it, what HTML or browser behavior it produces,
   its accessibility contract, and its most likely misuse. Examples must use public
   imports and safe values.
   Before inventing constructor conventions, compare the component with its siblings:
   container-like components accept positional nodes and `children=`, addressable
   wrappers use `id`, and `class_` augments rather than removes the built-in theme hook.
   Keep a nested child as a component in the render tree—never call its `render()` method
   or splice serialized HTML inside another built-in.
3. Give the component a useful preview in `demo_html()` or `static_demo()`. The preview
   must be semantic HTML that can be selected, focused, typed into, expanded, or
   otherwise inspected—not a screenshot. Verify it in both color schemes, at narrow
   width, at 200% zoom, with a keyboard, and with reduced motion.
4. If the component normally needs HTMX or a server response, set its `server` field and
   add a narrowly scoped handler in `docs/javascript/component-demos.js`. Simulate the
   pending, success, validation/empty, and recoverable failure states that matter to the
   component. Mark the request trace as simulated. Do not copy application
   authentication, authorization, CSRF, persistence, or data-access logic into the
   docs JavaScript; explain those server responsibilities on the page.
5. Add only reusable visual rules to
   `docs/stylesheets/component-demos.css`. Keep native semantics and visible focus;
   never make color, animation, or position the only state indicator.
6. Run the generator, add the new page to the Components section of `mkdocs.yml`, and
   run the coverage and docs checks:

   ```bash
   uv run python scripts/generate_component_docs.py
   uv run python scripts/generate_component_docs.py --check
   uv run --group docs mkdocs build --strict
   ```

7. Add a composition test, not only an isolated render assertion. Nest the component in
   its likely parent and place a likely child inside it. When it emits IDs, labels,
   ARIA references, HTMX targets, or swap boundaries, render repeated and nested
   instances and assert that IDs are unique and every relationship resolves. Also render
   it with the shipped default stylesheet in the browser at desktop and narrow widths.

The `--check` command compares the manifest with the implemented public built-ins,
rejects missing, stale, duplicate, or hand-edited generated pages, and is exercised by
the unit suite. Edit the manifest and regenerate rather than editing a generated
component page directly. When changing an existing constructor or behavior, update its
manifest entry and demo in the same change.

A component page is complete only when it includes a usable preview, a valid public
Python example, the constructor and parameter meanings, render/composition behavior,
the real backend/HTMX boundary, accessibility and focus behavior, security and
validation responsibilities, common mistakes, and a focused testing strategy.

Docs preview:

```bash
uv sync --group docs
uv run --group docs mkdocs serve
```

### Pull requests

- Keep changes focused; prefer small reviewable PRs.
- Do not bump coordinated package versions unless the change is a release cut.
- Add or update tests with behavior changes.
- For public API or security behavior, update the owning contract/docs in the same PR.

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
| `tests/` | Unit, integration, conformance, adapters |
| `examples/reference-app` | FastAPI cumulative example |
| `examples/flask-reference` | Flask slice |
| `examples/django-reference` | Django slice |

Release cutting is documented in [RELEASE](RELEASE.md). Project status lives in
[STATUS](STATUS.md).

---

## Contribute specifications

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

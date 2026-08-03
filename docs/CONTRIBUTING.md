# Contributing

## Contribute code

### Setup

```bash
git clone https://github.com/eddiethedean/hedron.git
cd hedron
uv sync
```

Workspace packages: `hedron-core`, `hedron`, `hedron-explorer`, `hedron-data`,
`hedron-charts`, `hedron-sample-kit`.

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
| `tests/` | Unit, integration, conformance |
| `examples/reference-app` | Cumulative example application |

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

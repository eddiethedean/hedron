# hedron-jinja

Explicit standards-first `.hdj` templates over Jinja, HTML, and HTMX.

**Package maturity:** Beta · **Train:** `0.45.x` (published `v0.45.0`) · pin `>=0.45.0,<0.46`
**Flagship extra:** `hedron[jinja]` · **Import:** `hedron_jinja`  
**Format:** HDJ v1 frozen · templates are **trusted application code**

## Install

```bash
pip install "hedron[jinja]>=0.45.0,<0.46"
# or
pip install "hedron-jinja>=0.45.0,<0.46"
```

Requires `hedron-core` and Jinja2.

## When to use

- Migrating HTML / Jinja apps with progressive Hedron adoption
- Ordinary Jinja inheritance/includes alongside typed Hedron components

Prefer typed Python components (`Page`, `Stack`, …) for new FastAPI apps unless you
already have a Jinja codebase. See [HDJ authoring](../guides/hdj-authoring.md).

## Quick start

```python
from jinja2 import Environment, FileSystemLoader
from hedron_jinja import HedronJinja, TemplateSpec

templates = HedronJinja(Environment(loader=FileSystemLoader("templates")))
result = templates.render(
    TemplateSpec("dashboard.hdj"),
    {"heading": "Operations"},
)
print(result.html)
```

Example `templates/dashboard.hdj`:

```hdj
---hdj
version = 1
kind = "fragment"
profile = "standard"
regions = ["main"]
---
<main id="main" hx-history-elt>{{ view.heading }}</main>
```

Register typed components when templates need them:

```python
from hedron_core import Badge

templates = HedronJinja(
    Environment(loader=FileSystemLoader("templates")),
    components={"Badge": Badge},
)
```

## Surfaces

| Surface | Role |
|---|---|
| `HedronJinja` | Environment wrapper; every `.hdj` renders through it |
| `TemplateSpec` | Trusted template identity, kind, and capabilities |
| `TemplateDeclaration` / `TemplateCapabilities` | Prologue / capability metadata |
| `HdjContext` | Template-side helper context (`hdj`) |
| `TwoPhaseStream` | Atomic render then body chunks (focused streaming) |
| Production inventory / CSP helpers | Deploy-time reconciliation aids |

## Trust model

- Templates are **not** a sandbox for hostile authors
- Strict mode checks a finite dynamic sink matrix with purpose-specific URL filters
- Deployment capability declarations and application policy remain authoritative
- Format v1 accepts static `.hdj` dependencies only

## Errors and failure modes

| Condition | Behavior |
|---|---|
| Async env + sync `render()` | Raises (`HED-JINJA-0014`) — use `render_async` |
| Undeclared async feature | Raises (`HED-JINJA-0023`) |
| Output over budget | Fail closed with output-limit diagnostic |
| Hostile / untrusted template authors | Out of scope — do not treat HDJ as a sandbox |

## Related docs

- Guide: [HDJ authoring](../guides/hdj-authoring.md)
- API: [HDJ (Jinja)](../api/JINJA.md)
- Migration: [FastAPI / Jinja + HTMX](../guides/fastapi-jinja-migration.md)
- Example: [hdj-progressive](https://github.com/eddiethedean/hedron/tree/main/examples/hdj-progressive)

## Links

- [PyPI](https://pypi.org/project/hedron-jinja/)
- [Changelog](https://github.com/eddiethedean/hedron/blob/main/packages/hedron-jinja/CHANGELOG.md)
- [Source](https://github.com/eddiethedean/hedron/tree/main/packages/hedron-jinja)

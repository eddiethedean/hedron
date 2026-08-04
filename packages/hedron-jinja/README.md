# hedron-jinja

HDJ is Hedron's explicit, standards-first `.hdj` format over Jinja for advanced applications.

```bash
pip install hedron-jinja
```

```python
from jinja2 import Environment, FileSystemLoader
from hedron_jinja import HedronJinja, TemplateSpec

templates = HedronJinja(
    Environment(loader=FileSystemLoader("templates")),
    components={"StatusBadge": StatusBadge},
)
result = templates.render(TemplateSpec("dashboard.hdj"), view)
```

```hdj
---hdj
version = 1
kind = "page"
profile = "standard"
regions = ["main"]
---
<main id="main" hx-history-elt>{{ view.heading }}</main>
```

Templates are trusted application code. Write ordinary HTML, CSS, JavaScript, Web Components,
Jinja, and HTMX directly; HDJ adds typed components and preserves Hedron render metadata. Strict
mode protects dynamic values and contracts without reducing the web platform. Deployment CSP and
security policy remain authoritative. The phase 0.9 format parser and complete feature/capability
checker are still being implemented. HDJ is not a sandbox for hostile template authors.

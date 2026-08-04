# hedron-jinja

Strict, typed Jinja authoring for Hedron applications.

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
result = templates.render(TemplateSpec("dashboard.html"), view)
```

Templates are trusted application code. Strict mode provides deterministic component bindings,
escaping, validation, metadata preservation, and bounded output; it is not a sandbox for hostile
template authors.

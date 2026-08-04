# Progressive HDJ examples

Install `hedron-jinja` (or `hedron[jinja]`) and run:

```bash
uv run python examples/hdj-progressive/app.py
```

| Template | Lesson |
|---|---|
| `01_minimal.hdj` | Three prologue fields, then ordinary HTML |
| `02_jinja.hdj` | Typed `view` fields with normal Jinja |
| `03_components.hdj` | `{% hedron %}` components and purpose-specific URL filters |

Templates are trusted application code. See the
[upgrade guide](../../docs/guides/upgrade.md) for the 0.8 → 0.9 HDN rewrite table.

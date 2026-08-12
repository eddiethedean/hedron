# Progressive HDJ examples

From a Hedron monorepo checkout:

```bash
uv sync
uv run python examples/hdj-progressive/app.py
```

Outside the monorepo:

```bash
pip install "hedron[jinja]>=0.29.0,<0.30"
# then run app.py from this directory with PYTHONPATH set appropriately
```

| Template | Lesson |
|---|---|
| `01_minimal.hdj` | Three prologue fields, then ordinary HTML |
| `02_jinja.hdj` | Typed `view` fields with normal Jinja |
| `03_components.hdj` | `{% hedron %}` components and purpose-specific URL filters |

Templates are trusted application code. See the
[upgrade guide](../../docs/guides/upgrade.md) for the 0.8 → 0.9 HDN rewrite table.

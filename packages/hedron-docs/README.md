# hedron-docs

Experimental Markdown compiler and Hedron application toolkit.

`hedron-docs` turns a bounded Markdown corpus into a deterministic JSON manifest and renders that
manifest through native Hedron components. The 0.1 surface is intentionally small and may change:

**Package maturity:** Beta tooling-grade · **Repository package version:** `0.1.0` · **Import:** `hedron_docs`

```python
from hedron_docs import compile_site, create_docs_app, load_config

config = load_config("hedron-docs.toml")
manifest = compile_site(config)
app = create_docs_app(manifest)
```

The package is not a drop-in MkDocs plugin. `import-mkdocs` reads site metadata and exclusions as
a migration aid; it never executes arbitrary MkDocs plugins or theme code.

```bash
hedron-docs check hedron-docs.toml
hedron-docs build hedron-docs.toml
hedron-docs serve hedron-docs.toml
hedron-docs import-mkdocs mkdocs.yml
```

This package is experimental and is not part of Hedron's stable support matrix.

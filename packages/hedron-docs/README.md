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

Local images and linked files are validated, fingerprinted, and embedded in the immutable manifest;
the app serves them from `/_hedron-docs/assets/...` with content hashes and bounded sizes.

```toml
[site]
title = "Project docs"
docs_dir = "docs"
base_url = "https://docs.example.com"

[build]
output = "build/hedron-docs/site.json"
max_source_bytes = 2000000
max_asset_bytes = 10000000
max_nodes = 10000
max_query_length = 200
```

The package is not a drop-in MkDocs plugin. `import-mkdocs` reads site metadata and exclusions as
a migration aid; it never executes arbitrary MkDocs plugins or theme code.

```bash
hedron-docs check hedron-docs.toml
hedron-docs build hedron-docs.toml
hedron-docs serve hedron-docs.toml
hedron-docs import-mkdocs mkdocs.yml
```

The repository proving app is available at `apps/hedron-docs/app.py:app` and can be started with
`uv run uvicorn --app-dir apps/hedron-docs app:app`.

This package is experimental and is not part of Hedron's stable support matrix.

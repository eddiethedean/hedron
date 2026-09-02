# hedron-docs

Experimental Markdown compiler and Hedron application toolkit.

`hedron-docs` turns a bounded Markdown corpus into a deterministic JSON manifest and renders that
manifest through native Hedron components. The 0.5 surface is intentionally experimental and may
change:

**Package maturity:** Beta tooling-grade · **Repository package version:** `0.5.0` · **Import:** `hedron_docs`

```python
from hedron_docs import compile_site, create_docs_app, load_config

config = load_config("hedron-docs.toml")
manifest = compile_site(config)
app = create_docs_app(manifest)
```

Local images and linked files are validated, fingerprinted, and embedded in the immutable manifest;
the app serves them from `/_hedron-docs/assets/...` with content hashes and bounded sizes.

```toml
schema_version = 4

[site]
title = "Project docs"
docs_dir = "docs"
base_url = "https://docs.example.com"

[build]
output = "build/hedron-docs/site.json"
max_source_bytes = 2000000
max_asset_bytes = 10000000
max_nodes = 10000
max_depth = 64
max_table_cells = 10000
max_code_blocks = 200
max_code_block_bytes = 256000
max_directives = 100
max_query_length = 200
```

The 0.4 compiler lowers CommonMark, tables, definition lists, footnotes, admonitions, details,
content tabs, API directives, and allowlisted demo references directly from parser tokens into a
closed typed AST, then renders them through native Hedron primitives. Headings expose stable alias
anchors; code and tables are responsive; code blocks include language labels and native copy
controls. Every parsed node carries a stable source span. Raw HTML and unknown extension syntax
fail with a diagnostic containing a code, title, location, explanation, and remediation.

The 0.5 application shell is Hedron-native: it provides accessible skip links and landmarks,
responsive primary/mobile navigation, breadcrumbs, release banners, source actions, and a
no-JavaScript color-mode preference form.

The package is not a drop-in MkDocs plugin. `import-mkdocs` reads site metadata, navigation, and
exclusions as a migration aid; it never executes arbitrary MkDocs plugins or theme code.

```bash
hedron-docs check hedron-docs.toml
hedron-docs build hedron-docs.toml
hedron-docs serve hedron-docs.toml
hedron-docs import-mkdocs mkdocs.yml
```

The repository proving app is available at `apps/hedron-docs/app.py:app` and can be started with
`uv run uvicorn --app-dir apps/hedron-docs app:app`.

This package is experimental and is not part of Hedron's stable support matrix.

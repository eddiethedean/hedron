# hedron-docs

Experimental Markdown compiler and Hedron documentation application toolkit.

**Package maturity:** Beta tooling-grade · **Repository package version:** `0.2.0` ·
pin `>=0.2.0,<0.3` · **Import:** `hedron_docs`

## Install

```bash
pip install "hedron-docs>=0.2.0,<0.3"
```

## Role

`hedron-docs` compiles bounded Markdown into a deterministic manifest and renders that manifest
through native Hedron components. It provides `check`, `build`, `serve`, and `import-mkdocs`
commands plus the `compile_site` and `create_docs_app` Python entry points.

Referenced local assets are jailed to the documentation root, size-bounded, fingerprinted, and
embedded in the immutable manifest. A deployable proving app lives at `apps/hedron-docs/app.py`.

The 0.2 compiler milestone provides direct token-to-AST parsing with stable source spans, a closed
typed node vocabulary, explicit extension nodes, schema-2 configuration/navigation import, and
bounded source, depth, node, table, code, and directive processing. It intentionally does not claim
full-corpus parity or production cutover.

The package is not a drop-in MkDocs plugin. MkDocs configuration is supported only as a bounded
migration input for site metadata, navigation, and exclusions; arbitrary plugins, hooks, theme
code, and request-time source parsing are not supported.

## Related docs

- [Native documentation implementation plan](https://github.com/eddiethedean/hedron/blob/main/docs/implementation/HEDRON_NATIVE_DOCUMENTATION.md)
- [RFC-0088](https://github.com/eddiethedean/hedron/blob/main/docs/rfcs/RFC-0088-HEDRON-NATIVE-DOCUMENTATION.md)

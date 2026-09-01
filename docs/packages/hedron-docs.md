# hedron-docs

Experimental Markdown compiler and Hedron documentation application toolkit.

**Package maturity:** Beta tooling-grade · **Repository package version:** `0.1.0` ·
pin `>=0.1.0,<0.2` · **Import:** `hedron_docs`

## Install

```bash
pip install "hedron-docs>=0.1.0,<0.2"
```

## Role

`hedron-docs` compiles bounded Markdown into a deterministic manifest and renders that manifest
through native Hedron components. It provides `check`, `build`, `serve`, and `import-mkdocs`
commands plus the `compile_site` and `create_docs_app` Python entry points.

The package is not a drop-in MkDocs plugin. MkDocs configuration is supported only as a bounded
migration input for site metadata and exclusions; arbitrary plugins, hooks, theme code, and
request-time source parsing are not supported.

## Related docs

- [Native documentation implementation plan](../implementation/HEDRON_NATIVE_DOCUMENTATION.md)
- [RFC-0088](../rfcs/RFC-0088-HEDRON-NATIVE-DOCUMENTATION.md)

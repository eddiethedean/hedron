# hedron-elements

**Package maturity:** Beta · **Train:** `0.57.x` (in-tree tip `v0.57.0`; PyPI `0.56.0`; 0.57.0 deferred) · application pin `>=0.56.0,<0.58`; repository checkouts use `uv sync`

Framework-neutral Web Component ABI and HTMX-safe bridge for Hedron. Includes the
`hedron-example` reference plus Beta form controls (`hedron-field-text`,
`hedron-field-choice`, `hedron-field-file`), primitives (`hedron-disclosure`,
`hedron-dialog`), and `hedron-action-async` with `InteractionState` (RFC-0060 /
D-064 / D-065).

```bash
pip install "hedron[elements]>=0.56.0,<0.58"
# or
pip install "hedron-elements>=0.56.0,<0.58"
```

Depends on `hedron-core` only. Host applications do not need Node.js.
The element tags are registered by the package plugin and are not Python component exports.
They remain Beta/production-grade for Supported inventory surfaces; pin the train and test the native/light-DOM fallback
on your browser matrix.

**0.40 author kit:** use public `PluginContext` registration and
`hedron_elements.author` helpers (or `hedron new element`). See
[Plugin authoring](https://hedron.readthedocs.io/en/latest/guides/plugin-authoring/) and
[`examples/element-author-plugin`](https://github.com/eddiethedean/hedron/tree/main/examples/element-author-plugin).
Optional `@hedron/elements` modules/types live under `npm/`; React-island remains
Experimental docs/reference only.

See the [implementation plan](https://github.com/eddiethedean/hedron/blob/main/docs/implementation/HEDRON_ELEMENTS_036.md)
and [0.37 extension plan](https://github.com/eddiethedean/hedron/blob/main/docs/implementation/HEDRON_ELEMENTS_037.md),
plus the [0.40 authoring plan](https://github.com/eddiethedean/hedron/blob/main/docs/implementation/HEDRON_AUTHORING_040.md)
and [platform spec](https://github.com/eddiethedean/hedron/blob/main/docs/implementation/WEB_COMPONENT_PLATFORM.md).

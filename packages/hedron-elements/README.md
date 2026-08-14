# hedron-elements

**Package maturity:** Alpha · **Train:** `0.40.x` · pin `>=0.40.0,<0.41`

Framework-neutral Web Component ABI and HTMX-safe bridge for Hedron. Includes the
`hedron-example` reference plus Alpha form controls (`hedron-field-text`,
`hedron-field-choice`, `hedron-field-file`), primitives (`hedron-disclosure`,
`hedron-dialog`), and `hedron-action-async` with `InteractionState` (RFC-0060 /
D-064 / D-065).

```bash
pip install "hedron[elements]>=0.40.0,<0.41"
# or
pip install "hedron-elements>=0.40.0,<0.41"
```

Depends on `hedron-core` only. Host applications do not need Node.js.
The element tags are registered by the package plugin and are not Python component exports.
They remain Alpha/incubator surfaces; pin the train and test the native/light-DOM fallback
on your browser matrix.

See the [implementation plan](https://github.com/eddiethedean/hedron/blob/main/docs/implementation/HEDRON_ELEMENTS_036.md)
and [0.37 extension plan](https://github.com/eddiethedean/hedron/blob/main/docs/implementation/HEDRON_ELEMENTS_037.md),
plus the [platform spec](https://github.com/eddiethedean/hedron/blob/main/docs/implementation/WEB_COMPONENT_PLATFORM.md).

# hedron-elements

**Package maturity:** Alpha · **Train:** `0.38.x` · pin `>=0.39.0,<0.40`

Framework-neutral Web Component ABI and HTMX-safe bridge. The package includes the
`hedron-example` ABI reference plus Alpha form controls (`hedron-field-text`,
`hedron-field-choice`, `hedron-field-file`), primitives (`hedron-disclosure`,
`hedron-dialog`), and `hedron-action-async` with `InteractionState` (RFC-0060 /
D-064 / D-065).

```bash
pip install "hedron[elements]>=0.39.0,<0.40"
pip install "hedron-elements>=0.39.0,<0.40"
```

Depends on `hedron-core` only. Applications do not need Node.js. Disposition in the
fleet inventory is `incubator` with production-grade destination **0.42**.

These tags are registered through the package plugin; they are not Python component exports.
They remain Alpha/incubator surfaces, and applications should test the light-DOM fallback and
form behavior on their supported browser matrix.

See [HEDRON_ELEMENTS_036](https://github.com/eddiethedean/hedron/blob/main/docs/implementation/HEDRON_ELEMENTS_036.md),
[HEDRON_ELEMENTS_037](https://github.com/eddiethedean/hedron/blob/main/docs/implementation/HEDRON_ELEMENTS_037.md), and
[WEB_COMPONENT_PLATFORM](https://github.com/eddiethedean/hedron/blob/main/docs/implementation/WEB_COMPONENT_PLATFORM.md).

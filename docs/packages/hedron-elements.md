# hedron-elements

**Package maturity:** Beta · **Train:** `0.47.x` (published `v0.47.0`) · pin `>=0.47.0,<0.48`

Framework-neutral Web Component ABI and HTMX-safe bridge. The package includes the
`hedron-example` ABI reference plus Beta form controls (`hedron-field-text`,
`hedron-field-choice`, `hedron-field-file`), primitives (`hedron-disclosure`,
`hedron-dialog`), and `hedron-action-async` with `InteractionState` (RFC-0060 /
D-064 / D-065).

From **0.40**, third parties author portable elements with the public author kit
(`hedron_elements.author`, `hedron new element`) and register via
`PluginContext.register_element_definition` / `register_asset`. Optional in-repo
`@hedron/elements` modules/TS types ship under `packages/hedron-elements/npm/` —
Python consumers still need no Node. React islands remain **Experimental
docs/reference only**
([react-island-reference](https://github.com/eddiethedean/hedron/blob/main/docs/implementation/react-island-reference/README.md)).

```bash
pip install "hedron[elements]>=0.47.0,<0.48"
pip install "hedron-elements>=0.47.0,<0.48"
```

Depends on `hedron-core` only. Applications do not need Node.js. Disposition in the
fleet inventory is `production-grade for Supported inventory` with production-grade destination **0.42**.

These tags are registered through the package plugin; they are not Python component exports.
They remain Beta/production-grade for Supported inventory surfaces, and applications should test the light-DOM fallback and
form behavior on their supported browser matrix.

See [What’s new in 0.41](../guides/whats-new-0.41.md),
[Plugin authoring](../guides/plugin-authoring.md),
[HEDRON_AUTHORING_040](https://github.com/eddiethedean/hedron/blob/main/docs/implementation/HEDRON_AUTHORING_040.md),
[HEDRON_ELEMENTS_036](https://github.com/eddiethedean/hedron/blob/main/docs/implementation/HEDRON_ELEMENTS_036.md),
[HEDRON_ELEMENTS_037](https://github.com/eddiethedean/hedron/blob/main/docs/implementation/HEDRON_ELEMENTS_037.md), and
[WEB_COMPONENT_PLATFORM](https://github.com/eddiethedean/hedron/blob/main/docs/implementation/WEB_COMPONENT_PLATFORM.md).

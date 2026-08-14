# Element author plugin (0.40)

Third-party-shaped element plugin that registers solely through public
`PluginContext` APIs (`first_party=False`). Evidence for `PLUGIN-040`.

## What it shows

- `ctx.register_asset` + `ctx.register_element_definition` without private registry imports
- Packaged static module/CSS for `ext-author-probe`
- Consumer verification via `verify_consumer.py`

## Run

From the Hedron workspace root:

```bash
uv run python examples/element-author-plugin/verify_consumer.py
```

## See also

- [Plugin authoring](https://hedron.readthedocs.io/en/latest/guides/plugin-authoring/)
- [What’s new in 0.40](https://hedron.readthedocs.io/en/latest/guides/whats-new-0.40/)
- [Plugins API](https://hedron.readthedocs.io/en/latest/api/PLUGINS/)

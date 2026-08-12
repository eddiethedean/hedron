# Sample-kit external consumer (PLUGIN-031)

Isolated consumer that discovers `hedron-sample-kit` via the `hedron.plugins`
entry point after a clean wheel install. Used by `scripts/check_plugin_031.py`.

## Manual check

```bash
uv build packages/hedron-sample-kit
uv run --with ./dist/hedron_sample_kit-*.whl python examples/sample-kit-consumer/verify_consumer.py
```

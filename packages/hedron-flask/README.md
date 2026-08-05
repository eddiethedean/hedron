# hedron-flask

Flask adapter for Hedron: render `Page` / `Fragment` components, map portable
`InteractionResult` values to native responses, and integrate CSRF double-submit
cookies with Flask sessions.

```bash
pip install "hedron-flask>=0.12.0"
```

Requires `hedron-core` and Flask 3.x. Does not install FastAPI. Current train:
**0.12.0** (Beta). Docs:
[Add to an existing Flask app](https://hedron.readthedocs.io/en/latest/getting-started/flask/).

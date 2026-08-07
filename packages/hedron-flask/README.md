# hedron-flask

Flask adapter for Hedron: render `Page` / `Fragment` components, map portable
`InteractionResult` values to native responses, and integrate CSRF double-submit
cookies with Flask sessions.

```bash
pip install "hedron-flask>=0.19.0,<0.20"
```

Requires `hedron-core` and Flask 3.x. Does not install FastAPI. Current train:
**0.19.0** (Beta; Ready to cut on `main`; last published PyPI/git = `v0.18.0`). Docs:
[Add to an existing Flask app](https://hedron.readthedocs.io/en/latest/getting-started/flask/).

# Flask recipe (Refresh)

Adopter recipe for Flask + Hedron HTMX Refresh. Full guide:
[Flask getting started](../getting-started/flask.md).

```bash
uvx --from "hedron>=0.22.0,<0.23" hedron new my-flask-app --flask
cd my-flask-app && uv sync && uv run flask --app app run
```

Open the app, click **Refresh**, and confirm the `#panel` timestamp updates without a
full reload. Next: [HTMX interactions](../guides/htmx-interactions.md) ·
[Ship to production](../guides/ship-to-production.md).

Monorepo reference (maintainers / evaluators):
[`examples/flask-reference`](https://github.com/eddiethedean/hedron/tree/main/examples/flask-reference).

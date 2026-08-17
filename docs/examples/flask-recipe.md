# Flask recipe (Refresh)

Adopter recipe for Flask + Hedron HTMX Refresh. Full guide:
[Flask getting started](../getting-started/flask.md).

```bash
uvx --from "hedron>=0.48.0,<0.49" hedron new my-flask-app --flask
cd my-flask-app && uv sync && uv run flask --app app run --port 8000
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000/), click **Refresh**, and confirm the
`#panel` timestamp updates without a full reload. Next: [HTMX interactions](../guides/htmx-interactions.md) ·
[Ship a Hedron app](../guides/ship.md).

Monorepo reference (maintainers / evaluators):
[`examples/flask-reference`](https://github.com/eddiethedean/hedron/tree/main/examples/flask-reference).

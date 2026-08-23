# Django recipe (Refresh)

Adopter recipe for Django + Hedron HTMX Refresh. Full guide:
[Django getting started](../getting-started/django.md).

```bash
uvx --from "hedron>=0.60.0,<0.61" hedron new my-django-app --django
cd my-django-app && uv sync
uv run waitress-serve --listen=127.0.0.1:8000 wsgi:application
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000/), click **Refresh**, and confirm the
`#panel` timestamp updates without a full reload. Next:
[HTMX interactions](../guides/htmx-interactions.md) ·
[Ship a Hedron app](../guides/ship.md).

Monorepo reference (maintainers / evaluators):
[`examples/django-reference`](https://github.com/eddiethedean/hedron/tree/main/examples/django-reference).

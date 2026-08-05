# hedron-django

Django adapter for Hedron: render components as `HttpResponse`, map portable
`InteractionResult` values, reverse URLs via Django's resolver, and document CSRF/session
integration through native middleware.

First-party bounded QuerySet `DataSource` and Django forms bridge are **Supported**
(D-046 / phase 0.11). Supply an already-authorized base QuerySet; omitted sort/filter
allowlists deny client refinements.

```bash
pip install "hedron-django>=0.13.0"
```

Requires `hedron-core` and Django **`>=5.2,<6`**. Does not install FastAPI. Install
`hedron_django.apps.HedronDjangoConfig` for system checks.

Current coordinated train: **`0.13.0`** (Beta). See
[Add to an existing Django project](https://hedron.readthedocs.io/en/latest/getting-started/django/).

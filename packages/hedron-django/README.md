# hedron-django

Django adapter for Hedron: render components as `HttpResponse`, map portable
`InteractionResult` values, reverse URLs via Django's resolver, and document CSRF/session
integration through native middleware.

QuerySet `DataSource` is explicitly deferred (D-036).

```bash
pip install "hedron-django>=0.10.1"
```

Requires `hedron-core` and Django **`>=5.2,<6`**. Does not install FastAPI.

Current coordinated train: **`0.10.1`** (Beta). See
[Add to an existing Django project](https://hedron.readthedocs.io/en/latest/getting-started/django/).

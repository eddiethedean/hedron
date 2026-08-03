# hedron-django

Django adapter for Hedron: render components as `HttpResponse`, map portable
`InteractionResult` values, reverse URLs via Django's resolver, and document CSRF/session
integration through native middleware.

QuerySet `DataSource` is explicitly deferred (D-036).

```bash
pip install hedron-django
```

Requires `hedron-core` and Django 5.x. Does not install FastAPI.

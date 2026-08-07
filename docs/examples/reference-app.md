# Reference app walkthrough

Annotated tour of
[`examples/reference-app`](https://github.com/eddiethedean/hedron/tree/main/examples/reference-app)—
the FastAPI flagship CRUD sample on the **0.19.0** train.

## Run

```bash
git clone https://github.com/eddiethedean/hedron.git
cd hedron
uv sync
uv run uvicorn app:app --app-dir examples/reference-app --reload
```

Sign in with HTTP Basic: **`admin` / `secret`**.

## What the app demonstrates

| Concern | Where to look (`examples/reference-app/`) |
|---|---|
| `Hedron()` app + security profile | `app.py` → `build_hedron_app()` |
| Session/user gate | `require_user` + router `dependencies=[Depends(require_user)]` |
| CSRF on forms | `csrf_token_for_request` + hidden field / `hx-headers` in `_create_form` |
| Create user POST | `@users.action("", method="POST")` |
| Fragment table refresh | `@users.component("/table")`, addressable `user_table` |
| DataEditor / Auto / charts | dashboard sections and `/charts/*` routes |
| Color mode | `ColorModeToggle` + preference cookie helpers |

## Suggested reading order in the code

1. `build_hedron_app()` — how the app is constructed and the build dir is prepared
2. `home` page handler — CSRF token issuance for the dashboard
3. `_create_form` — progressive form with HTMX target on `#user-table`
4. User create/update/delete actions — validation, store mutation, fragment returns
5. Chart routes — `InteractionResult` + declared fragment regions

## Related guides

- [Forms and actions](../guides/forms-and-actions.md)
- [Authentication](../guides/authentication.md)
- [HTMX interactions](../guides/htmx-interactions.md)
- [Charts and HTMX](../guides/charts-and-htmx.md)
- [Plain FastAPI + HedronRouter](../guides/plain-fastapi.md)

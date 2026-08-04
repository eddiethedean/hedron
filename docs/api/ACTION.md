---
status: shipped
---

# `Action`


!!! note "Stability (0.8 freeze)"

    Classifications for this surface are recorded in [STABILITY.md](STABILITY.md). Package maturity (Beta/Alpha) is separate from API level (`beta` / `experimental` / `internal` / `deferred`).

**Status:** Accepted

An action is a typed server operation bound to UI controls and normal FastAPI request processing.

```python
@users.action("/{user_id}", method="DELETE")
async def delete_user(
    user_id: int,
    current_user: User = Depends(require_admin),
) -> UserTable:
    await service.delete(user_id)
    return UserTable(rows=await service.list_users(current_user.team_id))
```

## Contract

- Method, route, input contract, dependencies, and return behavior are explicit.
- Hedron may infer URL, target, swap, CSRF mechanics, loading state, and validation-fragment handling from registration.
- It never infers permission, destructive meaning, confirmation policy, or persistence.
- GET actions cannot mutate by contract.
- Unsafe cookie-authenticated actions include and validate CSRF protection. Tokens may be supplied via the `X-CSRF-Token` header or the `csrf_token` form field and must match the `hedron_csrf` cookie. The cookie is issued on safe GETs and reused (not rotated) for subsequent requests in the same session.
- Local redirects reject untrusted external destinations; external redirects use `redirect_external` and require an enabling security policy.

Actions may return components, explicit responses, redirects, or structured results that set approved HTMX headers via `approved_headers(...)`.

Background work attached to the response uses FastAPI `BackgroundTasks`; durable work returns or references a job resource.

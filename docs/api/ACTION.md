# `Action`

**Status:** Proposed

An action is a typed server operation bound to UI controls and normal FastAPI request processing.

```python
@users.action("/{user_id}", method="DELETE")
async def delete_user(
    user_id: int,
    current_user: User = Depends(require_admin),
) -> UserTable:
    await service.delete(user_id)
    return await user_table(...)
```

## Contract

- Method, route, input contract, dependencies, and return behavior are explicit.
- Hedron may infer URL, target, swap, CSRF mechanics, loading state, and validation-fragment handling from registration.
- It never infers permission, destructive meaning, confirmation policy, or persistence.
- GET actions cannot mutate by contract.
- Unsafe cookie-authenticated actions include and validate CSRF protection.

Actions may return components, explicit responses, redirects, or structured action results that set approved HTMX headers. Local redirects reject untrusted external destinations; external redirects use a distinct explicit API.

Background work attached to the response uses FastAPI `BackgroundTasks`; durable work returns or references a job resource.


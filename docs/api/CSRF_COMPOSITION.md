---
status: shipped
---

# CSRF and SecurityPolicy composition (0.22)

!!! note "Shipped — phase 0.22"

    Pluggable CSRF strategies, composable security headers, and `CsrfField` /
    `Form(hx=...)` are available on the **0.22** train. Living CSRF overview:
    [Security types](SECURITY_TYPES.md) and [Security guide](../guides/security.md).
    Acceptance: [RELEASE_0_22](../acceptance/RELEASE_0_22.md) ·
    [release-gate-0.22.toml](../acceptance/release-gate-0.22.toml).

Owning decision: **D-051**. Closed issues (shipped in 0.22):
[#36](https://github.com/eddiethedean/hedron/issues/36),
[#37](https://github.com/eddiethedean/hedron/issues/37),
[#38](https://github.com/eddiethedean/hedron/issues/38).

## Goals

1. Plug CSRF strategies without requiring Starlette cookie sessions (`CSRF-022`).
2. Merge/override security headers per name without `security_headers=False` (`HEADERS-022`).
3. First-class `CsrfField` and HTMX kwargs on `Form` (`FORM-022`).

## `CSRF-022` — strategy protocol

Portable types live in `hedron-core` (re-exported from `hedron`).

```python
from hedron import (
    DoubleSubmitCookieCsrf,
    SessionTokenCsrf,
    SecurityPolicy,
)

policy = SecurityPolicy(
    csrf=SessionTokenCsrf(
        get_expected=lambda request: request.state.auth.session.csrf_token,
        form_field="csrf_token",
        header_name="X-CSRF-Token",
    ),
)
```

`SecurityPolicy.resolve_csrf_strategy()` returns the active strategy, or `None` when
`csrf_enabled=False`. Named profiles keep Compatible double-submit behavior via
`DoubleSubmitCookieCsrf`.

| Strategy | Role |
|---|---|
| `DoubleSubmitCookieCsrf` | Default cookie double-submit |
| `SessionTokenCsrf` | App-owned synchronizer via `get_expected(request)` |

Pre-auth login helpers (`issue_login_csrf` / `validate_login_csrf`) remain a separate
composition path — not a second mandatory protocol.

### Adapter matrix (CSRF)

| Host | 0.22 expectation |
|---|---|
| FastAPI (`hedron`) | Full strategy wiring on unsafe routes |
| Flask (`hedron-flask`) | Double-submit helpers remain |
| Django (`hedron-django`) | `CsrfViewMiddleware` stays authoritative for validation |

## `HEADERS-022` — composable headers

```python
from hedron import SecurityHeadersPolicy, SecurityPolicy

SecurityPolicy(
    security_headers=SecurityHeadersPolicy(
        content_security_policy="default-src 'self'; ...",
        hsts_max_age=31536000,
        # Unspecified fields keep profile defaults.
    ),
)
# Escape hatch when the host owns all headers:
# SecurityPolicy(security_headers=False)  # or security_headers="app"
```

Merge runs inside `SecurityPolicy.response_headers()` — FastAPI / Flask / Django
applicators need no parallel middleware.

## `FORM-022` — `CsrfField` and Form HTMX kwargs

```python
from hedron import CsrfField, Form, Hx, csrf_token_for_request

Form(
    CsrfField(token=csrf_token_for_request(request, policy)),
    # or CsrfField() when RenderContext carries csrf_token (FastAPI pages do)
    FormField(...),
    action="/save",
    method="post",
    hx=Hx(target="#profile-form-region", swap="outerHTML", indicator="#busy"),
)
```

`Form(**{"hx-post": ...})` stringly attrs remain supported as an escape hatch.

## Errors

| Condition | Behavior |
|---|---|
| Missing / invalid CSRF on unsafe method | HTTP **403** (built-in profiles with CSRF enabled) |
| `CsrfField()` without token and without page `RenderContext.csrf_token` | `ValueError` at render time |
| `security_headers=False` / `"app"` | Hedron skips applying profile headers — host owns them |
| Strategy `get_expected` returns no match | Validation fails closed (403) |

Human index: [Error codes](../guides/error-codes.md). First-hour form:
[Minimal form POST](../guides/minimal-form.md).

## Evidence

| Gate | Intent |
|---|---|
| `CSRF-022` | Protocol + non-Starlette strategy + FastAPI validate tests |
| `HEADERS-022` | Merge/override on FastAPI (+ adapter applicator reuse) |
| `FORM-022` | `CsrfField` + Form HTMX kwargs docs/tests |
| `REGRESS-022` / `PKG-022` | Full suite and packet verify at cut |


## Django form field

Django's `CsrfViewMiddleware` accepts **`csrfmiddlewaretoken`**, not the portable FastAPI/Flask default `csrf_token`. The Django adapter seeds `RenderContext` with `csrf_form_field="csrfmiddlewaretoken"` so bare `CsrfField()` works.

## Login CSRF

Pre-auth login forms use `LoginCsrfField` / `issue_login_csrf` / `validate_login_csrf` — not plain `CsrfField()` (post-auth strategy token).

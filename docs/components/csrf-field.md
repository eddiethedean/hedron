---
title: CsrfField
description: Hidden CSRF input wired to the active strategy or an explicit token.
---

# `CsrfField`

Hidden CSRF input wired to the active strategy or an explicit token.

| | |
|---|---|
| Import | `from hedron import CsrfField` |
| Distribution | `hedron` |
| Backend activity | On submit |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

=== "Demo"

    Docs simulation — not a running Hedron server. Interactive demos show a “Simulated HTMX” trace when applicable.

    <!-- hedron-sim:component-form -->

=== "Code"

    Minimal runnable `app.py` that reproduces this demo (real Hedron, not the docs simulator):

    ```python title="app.py"
    from __future__ import annotations

    import json
    import os

    from fastapi import Request
    from pydantic import ValidationError

    from hedron import (
        Field,
        Form,
        FormErrors,
        FormField,
        FormModel,
        Hedron,
        InteractionResult,
        Page,
        Stack,
        SubmitButton,
        Text,
        TextInput,
        html,
    )
    from hedron.security import csrf_token_for_request

    app = Hedron(
        title="Form demo",
        security="standard",
        explorer="off",
        session_secret=os.environ.get("HEDRON_SESSION_SECRET", "dev-only"),
    )

    region = app.region("demo-form")


    class Invite(FormModel):
        email: str = Field(min_length=3, label="Email address")


    def _csrf(request: Request) -> str:
        return csrf_token_for_request(request, request.app.state.hedron_security)


    def form_body(*, csrf_token: str, errors: tuple[str, ...] = ()):
        return html.div(
            Form(
                FormErrors(errors),
                html.input(type="hidden", name="csrf_token", value=csrf_token),
                FormField(
                    name="email",
                    label="Email address",
                    control=TextInput(name="email", placeholder="ada@example.com"),
                ),
                SubmitButton("Submit"),
                **{
                    "hx-post": "/demo",
                    "hx-target": region.selector,
                    "hx-swap": "outerHTML",
                    "hx-headers": json.dumps({"X-CSRF-Token": csrf_token}),
                },
            ),
            id=region.id,
        )


    @app.page("/")
    def home(request: Request) -> Page:
        return Page(Stack(form_body(csrf_token=_csrf(request))), title="Form")


    @app.component("/demo", methods=["POST"], fragment_regions=(region,))
    async def submit(request: Request) -> InteractionResult:
        form = await request.form()
        try:
            data = Invite.model_validate({"email": form.get("email", "")})
        except ValidationError:
            return InteractionResult(
                content=form_body(
                    csrf_token=_csrf(request),
                    errors=("Enter a valid work email.",),
                ),
                status_code=422,
                region_id=region.id,
            )
        return InteractionResult(
            content=html.div(
                html.strong("Submitted"),
                Text(f"Queued for {data.email}."),
                id=region.id,
                role="status",
            ),
            region_id=region.id,
        )
    ```


## Basic use

```python
from hedron import CsrfField

component = CsrfField(token=csrf_token_for_request(request, policy))
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

Use inside Form for POST/HTMX mutations. Prefer explicit token= in portable/offline renders.

This component can initiate or represent a backend interaction. The live documentation intercepts that interaction with JavaScript and shows the same pending, success, or replacement states without making a real request. In an application, keep the URL, authorization, validation, and returned fragment on the server; JavaScript is only progressive enhancement.

## Constructor and parameters

```python
CsrfField(*, name=None, token=None)
```

| Parameter | Type | Meaning |
|---|---|---|
| `name` | `str | None` | Form field name; defaults to the strategy / RenderContext field. |
| `token` | `str | None` | Token value; when omitted, uses RenderContext.csrf_token on FastAPI pages. |

## Composition and backend behavior

Keep `CsrfField` at the smallest semantic boundary. Fragment routes should return only
the replaced region and preserve stable target IDs across success, validation, empty,
loading, and error responses.

Mutating flows must use POST, validate CSRF, authorize on the server, re-validate typed input, and return a bounded fragment. GET remains safe and repeatable; native submit should still work without HTMX.

## Accessibility

The field is aria-hidden by nature as a hidden input; pair with visible validation feedback on failure.

## Security

Escaping and `SafeUrl` / `TrustedHtml` are framework concerns; authorization and data
exposure remain application code. Redact secrets before rendering.

## Common mistakes

- Never log or display the token value in diagnostics.
- Do not copy docs-preview JavaScript into an application server.

## Testing

```python
from hedron import RenderMode, render

result = render(component, mode=RenderMode.FRAGMENT)
assert result.html
assert not result.diagnostics
```

[All component demos](index.md) · [Built-in API](../api/BUILT_INS.md) · [Testing](../guides/testing.md)

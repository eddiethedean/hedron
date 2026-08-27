---
title: FormErrors
description: Summarize one or more form-level validation errors.
---

# `FormErrors`

Summarize one or more form-level validation errors.

| | |
|---|---|
| Import | `from hedron import FormErrors` |
| Distribution | `hedron` |
| Backend activity | No |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

=== "Demo"

    Docs simulation — not a running Hedron server. Interactive demos show a “Simulated HTMX” trace when applicable.

    <!-- hedron-sim:component-form-errors -->

=== "Code"

    Minimal runnable `app.py` that reproduces this demo (real Hedron, not the docs simulator):

    ```python title="app.py"
    import os

    from hedron import FormErrors, Hedron, InteractionResult, Page, Stack, html

    app = Hedron(
        title="FormErrors demo",
        security="standard",
        explorer="off",
        session_secret=os.environ.get("HEDRON_SESSION_SECRET", "dev-only"),
    )

    region = app.region("errors-demo")
    slot = app.region("errors-slot")


    @app.page("/")
    def home() -> Page:
        return Page(
            Stack(
                html.div(
                    html.p("Submit with missing fields to redisplay FormErrors."),
                    html.div(id=slot.id),
                    html.button(
                        "Submit empty form",
                        type="button",
                        **{
                            "hx-post": "/invite",
                            "hx-target": slot.selector,
                            "hx-swap": "innerHTML",
                        },
                    ),
                    id=region.id,
                ),
            ),
            title="FormErrors",
        )


    @app.action("/invite", method="POST", fragment_regions=(region, slot))
    def fail() -> InteractionResult:
        return InteractionResult(
            content=FormErrors(["Email is required.", "Choose a billing plan."]),
            status_code=422,
            region_id=slot.id,
        )
    ```


## Basic use

```python
from hedron import FormErrors

component = FormErrors(['Email is required.', 'Choose a billing plan.'])
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

An empty sequence renders nothing. Otherwise errors become a list inside an alert region so a failed response is announced.

This component can initiate or represent a backend interaction. The live documentation intercepts that interaction with JavaScript and shows the same pending, success, or replacement states without making a real request. In an application, keep the URL, authorization, validation, and returned fragment on the server; JavaScript is only progressive enhancement.

## Constructor and parameters

```python
FormErrors(errors)
```

| Parameter | Type | Meaning |
|---|---|---|
| `errors` | `Sequence[str]` | Ordered human-readable error messages. |

## Composition and backend behavior

Keep `FormErrors` at the smallest semantic boundary. Fragment routes should return only
the replaced region and preserve stable target IDs across success, validation, empty,
loading, and error responses.

Mutating flows must use POST, validate CSRF, authorize on the server, re-validate typed input, and return a bounded fragment. GET remains safe and repeatable; native submit should still work without HTMX.

## Accessibility

Put the summary before the fields and also attach each field-specific error with FormField.

## Security

Escaping and `SafeUrl` / `TrustedHtml` are framework concerns; authorization and data
exposure remain application code. Redact secrets before rendering.

## Common mistakes

- Do not include raw exception messages or sensitive submitted values.
- Do not copy docs-preview JavaScript into an application server.

## Testing

```python
from hedron import RenderMode, render

result = render(component, mode=RenderMode.FRAGMENT)
assert result.html
assert not result.diagnostics
```

[All component demos](index.md) · [Built-in API](../api/BUILT_INS.md) · [Testing](../guides/testing.md)

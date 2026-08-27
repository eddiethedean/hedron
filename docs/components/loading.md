---
title: Loading
description: Show a polite busy status while a request or deferred component is pending.
---

# `Loading`

Show a polite busy status while a request or deferred component is pending.

| | |
|---|---|
| Import | `from hedron import Loading` |
| Distribution | `hedron` |
| Backend activity | No |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

=== "Demo"

    Docs simulation — not a running Hedron server. Interactive demos show a “Simulated HTMX” trace when applicable.

    <!-- hedron-sim:component-loading -->

=== "Code"

    Minimal runnable `app.py` that reproduces this demo (real Hedron, not the docs simulator):

    ```python title="app.py"
    import os

    from hedron import Hedron, Loading, Page, Stack, html, swap

    app = Hedron(
        title="Loading demo",
        security="standard",
        explorer="off",
        session_secret=os.environ.get("HEDRON_SESSION_SECRET", "dev-only"),
    )

    box = app.region("loading-target")


    @app.page("/")
    def home() -> Page:
        return Page(
            Stack(
                html.div(Loading("Loading account activity…"), id=box.id),
                html.button(
                    "Load activity",
                    type="button",
                    **{
                        "hx-get": "/activity",
                        "hx-target": box.selector,
                        "hx-swap": "innerHTML",
                    },
                ),
            ),
            title="Loading",
        )


    @app.view("/activity", fragment_regions=(box,))
    def load():
        return swap(
            html.div(
                html.strong("3 events"),
                html.span("Deployment, approval, and release notes."),
                role="status",
            )
        )
    ```


## Basic use

```python
from hedron import Loading

component = Loading('Loading account activity…')
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

Loading emits a status region with polite live and busy semantics. It is frequently used as Lazy or Poll content and as an HTMX indicator.

This component can initiate or represent a backend interaction. The live documentation intercepts that interaction with JavaScript and shows the same pending, success, or replacement states without making a real request. In an application, keep the URL, authorization, validation, and returned fragment on the server; JavaScript is only progressive enhancement.

## Constructor and parameters

```python
Loading(message='Loading…')
```

| Parameter | Type | Meaning |
|---|---|---|
| `message` | `str` | Specific progress message. |

## Composition and backend behavior

Keep `Loading` at the smallest semantic boundary. Fragment routes should return only
the replaced region and preserve stable target IDs across success, validation, empty,
loading, and error responses.

Mutating flows must use POST, validate CSRF, authorize on the server, re-validate typed input, and return a bounded fragment. GET remains safe and repeatable; native submit should still work without HTMX.

## Accessibility

Name the operation when several requests could be active; remove or replace the status when work completes.

## Security

Escaping and `SafeUrl` / `TrustedHtml` are framework concerns; authorization and data
exposure remain application code. Redact secrets before rendering.

## Common mistakes

- Do not use Loading for indeterminate work that has failed—render ErrorState.
- Do not copy docs-preview JavaScript into an application server.

## Testing

```python
from hedron import RenderMode, render

result = render(component, mode=RenderMode.FRAGMENT)
assert result.html
assert not result.diagnostics
```

[All component demos](index.md) · [Built-in API](../api/BUILT_INS.md) · [Testing](../guides/testing.md)

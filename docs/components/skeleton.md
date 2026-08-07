---
title: Skeleton
description: Reserve space for content that is still loading.
---

# `Skeleton`

Reserve space for content that is still loading.

| | |
|---|---|
| Import | `from hedron import Skeleton` |
| Distribution | `hedron` |
| Backend activity | No |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

=== "Demo"

    Docs simulation — not a running Hedron server. Interactive demos show a “Simulated HTMX” trace when applicable.

    <!-- hedron-sim:component-skeleton -->

=== "Code"

    Minimal runnable `app.py` that reproduces this demo (real Hedron, not the docs simulator):

    ```python title="app.py"
    import os

    from hedron import Hedron, Page, Skeleton, Stack, html, swap

    app = Hedron(
        title="Skeleton demo",
        security="standard",
        explorer="off",
        session_secret=os.environ.get("HEDRON_SESSION_SECRET", "dev-only"),
    )

    box = app.region("skeleton-target")


    @app.page("/")
    def home() -> Page:
        return Page(
            Stack(
                html.div(Skeleton(lines=3), id=box.id),
                html.button(
                    "Load profile",
                    type="button",
                    **{
                        "hx-get": "/profile",
                        "hx-target": box.selector,
                        "hx-swap": "innerHTML",
                    },
                ),
            ),
            title="Skeleton",
        )


    @app.fragment("/profile", region=box)
    def load():
        return swap(
            html.div(
                html.strong("Ada Lovelace"),
                html.span("Platform · Active"),
                role="status",
            )
        )
    ```


## Basic use

```python
from hedron import Skeleton

component = Skeleton(lines=4)
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

Skeleton emits the requested placeholder lines, hides each line from the accessibility tree, and marks the wrapper busy. Pair it with a separate status message or the Loading component when users need progress context.

This component can initiate or represent a backend interaction. The live documentation intercepts that interaction with JavaScript and shows the same pending, success, or replacement states without making a real request. In an application, keep the URL, authorization, validation, and returned fragment on the server; JavaScript is only progressive enhancement.

## Constructor and parameters

```python
Skeleton(*, lines=3)
```

| Parameter | Type | Meaning |
|---|---|---|
| `lines` | `int` | Number of presentation-only placeholder rows. |

## Composition and backend behavior

Keep `Skeleton` at the smallest semantic boundary. Fragment routes should return only
the replaced region and preserve stable target IDs across success, validation, empty,
loading, and error responses.

Mutating flows must use POST, validate CSRF, authorize on the server, re-validate typed input, and return a bounded fragment. GET remains safe and repeatable; native submit should still work without HTMX.

## Accessibility

Because the visual lines are hidden semantically, provide an adjacent live status for meaningful waits.

## Security

Escaping and `SafeUrl` / `TrustedHtml` are framework concerns; authorization and data
exposure remain application code. Redact secrets before rendering.

## Common mistakes

- Validate `lines` in application configuration; zero or negative values produce an empty busy wrapper rather than a useful placeholder.
- Do not copy docs-preview JavaScript into an application server.

## Testing

```python
from hedron import RenderMode, render

result = render(component, mode=RenderMode.FRAGMENT)
assert result.html
assert not result.diagnostics
```

[All component demos](index.md) · [Built-in API](../api/BUILT_INS.md) · [Testing](../guides/testing.md)

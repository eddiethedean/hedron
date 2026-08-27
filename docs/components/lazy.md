---
title: Lazy
description: Load a component fragment when its placeholder enters the document.
---

# `Lazy`

Load a component fragment when its placeholder enters the document.

| | |
|---|---|
| Import | `from hedron import Lazy` |
| Distribution | `hedron` |
| Backend activity | Immediately after load |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

=== "Demo"

    Docs simulation — not a running Hedron server. Interactive demos show a “Simulated HTMX” trace when applicable.

    <!-- hedron-sim:component-lazy -->

=== "Code"

    Minimal runnable `app.py` that reproduces this demo (real Hedron, not the docs simulator):

    ```python title="app.py"
    import os

    from hedron import ComponentRef, Hedron, Lazy, Loading, Page, html, swap

    app = Hedron(
        title="Lazy demo",
        security="standard",
        explorer="off",
        session_secret=os.environ.get("HEDRON_SESSION_SECRET", "dev-only"),
    )

    box = app.region("lazy-box")
    ref = ComponentRef(
        logical_id="activity-feed",
        path="/activity-feed",
        target=box.selector,
        swap="innerHTML",
    )


    @app.page("/")
    def home() -> Page:
        return Page(
            Lazy(
                ref=ref,
                placeholder=Loading("Loading account activity…"),
                target_id=box.id,
            ),
            title="Lazy",
        )


    @app.view("/activity-feed", fragment_regions=(box,))
    def feed():
        return swap(
            html.div(
                html.strong("3 recent events"),
                html.span("Deployment, approval, and release notes loaded."),
            )
        )
    ```


## Basic use

```python
from hedron import Lazy, Skeleton

component = Lazy(ref=ComponentRef('activity-feed'), placeholder=Skeleton(lines=3), target_id='activity-feed')
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

Lazy emits a load-triggered HTMX request that swaps into an inner `#…-body` wrapper so a `template[data-hedron-error-template]` survives a successful load. `hedron-ui.mjs` (core and FastAPI copies, kept byte-identical) rematerializes the template on `htmx:responseError` / `htmx:sendError`.

This component can initiate or represent a backend interaction. The live documentation intercepts that interaction with JavaScript and shows the same pending, success, or replacement states without making a real request. In an application, keep the URL, authorization, validation, and returned fragment on the server; JavaScript is only progressive enhancement.

## Constructor and parameters

```python
Lazy(*, ref, placeholder=None, target_id=None, error=None)
```

| Parameter | Type | Meaning |
|---|---|---|
| `ref` | `ComponentRef` | Typed fragment endpoint. |
| `placeholder` | `NodeLike | None` | Initial content; defaults to Loading. |
| `target_id` | `str | None` | Explicit host ID; generated collision-free by default. |
| `error` | `NodeLike | None` | Error template kept outside the inner `#…-body` swap target. |

## Composition and backend behavior

Keep `Lazy` at the smallest semantic boundary. Fragment routes should return only
the replaced region and preserve stable target IDs across success, validation, empty,
loading, and error responses.

Mutating flows must use POST, validate CSRF, authorize on the server, re-validate typed input, and return a bounded fragment. GET remains safe and repeatable; native submit should still work without HTMX.

## Accessibility

Choose a placeholder that reserves approximately the final space and provide meaningful loading text for material waits.

## Security

Escaping and `SafeUrl` / `TrustedHtml` are framework concerns; authorization and data
exposure remain application code. Redact secrets before rendering.

## Common mistakes

- Do not lazy-load content needed to understand or operate the initial page without a robust failure state.
- Do not copy docs-preview JavaScript into an application server.

## Testing

```python
from hedron import RenderMode, render

result = render(component, mode=RenderMode.FRAGMENT)
assert result.html
assert not result.diagnostics
```

[All component demos](index.md) · [Built-in API](../api/BUILT_INS.md) · [Testing](../guides/testing.md)

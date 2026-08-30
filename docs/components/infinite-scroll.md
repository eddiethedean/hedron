---
title: InfiniteScroll
description: Append the next fragment when a pagination sentinel is revealed.
---

# `InfiniteScroll`

Append the next fragment when a pagination sentinel is revealed.

| | |
|---|---|
| Import | `from hedron import InfiniteScroll` |
| Distribution | `hedron` |
| Backend activity | When revealed |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

=== "Demo"

    Docs simulation — not a running Hedron server. Interactive demos show a “Simulated HTMX” trace when applicable.

    <!-- hedron-sim:component-infinite -->

=== "Code"

    Minimal runnable `app.py` that reproduces this demo (real Hedron, not the docs simulator):

    ```python title="app.py"
    import os

    from hedron import ComponentRef, Fragment, Hedron, InfiniteScroll, Page, Stack, html, swap

    app = Hedron(
        title="InfiniteScroll demo",
        security="standard",
        explorer="off",
        session_secret=os.environ.get("HEDRON_SESSION_SECRET", "dev-only"),
    )

    feed = app.region("event-feed")
    ref = ComponentRef(
        logical_id="events",
        path="/events",
        target=feed.selector,
        swap="beforeend",
    )


    @app.page("/")
    def home() -> Page:
        return Page(
            Stack(
                html.ol(
                    html.li("Deployment completed"),
                    html.li("Review approved"),
                    id=feed.id,
                ),
                InfiniteScroll(ref=ref, target=feed.selector, swap="beforeend"),
            ),
            title="InfiniteScroll",
        )


    @app.view("/events", fragment_regions=(feed,))
    def more():
        return swap(Fragment(html.li("Tests passed"), html.li("Release published")))
    ```


## Basic use

```python
from hedron import ComponentRef, InfiniteScroll
component = InfiniteScroll(ref=ComponentRef('next-events', '/events', params={'page': 2}), target='#event-list')
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

The sentinel uses HTMX's revealed trigger and appends to the selected collection. The response should contain new records plus the next sentinel, or omit the sentinel when no pages remain.

This component can initiate or represent a backend interaction. The live documentation intercepts that interaction with JavaScript and shows the same pending, success, or replacement states without making a real request. In an application, keep the URL, authorization, validation, and returned fragment on the server; JavaScript is only progressive enhancement.

## Constructor and parameters

```text
InfiniteScroll(*, ref, target, swap='beforeend')
```

| Parameter | Type | Meaning |
|---|---|---|
| `ref` | `ComponentRef` | Typed next-page endpoint. |
| `target` | `safe CSS selector` | Collection receiving appended nodes. |
| `swap` | `str` | Usually `beforeend`. |

## Composition and backend behavior

Keep `InfiniteScroll` at the smallest semantic boundary. Fragment routes should return only
the replaced region and preserve stable target IDs across success, validation, empty,
loading, and error responses.

Mutating flows must use POST, validate CSRF, authorize on the server, re-validate typed input, and return a bounded fragment. GET remains safe and repeatable; native submit should still work without HTMX.

## Accessibility

Provide a visible Load more fallback and announce how many items were added without moving focus.

## Security

Escaping and `SafeUrl` / `TrustedHtml` are framework concerns; authorization and data
exposure remain application code. Redact secrets before rendering.

## Common mistakes

- Do not create an endless keyboard or screen-reader experience with no way to reach following page content.
- Do not copy docs-preview JavaScript into an application server.

## Testing

```python
from hedron import RenderMode, render

result = render(component, mode=RenderMode.FRAGMENT)
assert result.html
assert not result.diagnostics
```

[All component demos](index.md) · [Built-in API](../api/BUILT_INS.md) · [Testing](../guides/testing.md)

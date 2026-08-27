---
title: Poll
description: Refresh a fragment at a bounded interval while it remains in the DOM.
---

# `Poll`

Refresh a fragment at a bounded interval while it remains in the DOM.

| | |
|---|---|
| Import | `from hedron import Poll` |
| Distribution | `hedron` |
| Backend activity | On every interval |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

=== "Demo"

    Docs simulation — not a running Hedron server. Interactive demos show a “Simulated HTMX” trace when applicable.

    <!-- hedron-sim:component-poll -->

=== "Code"

    Minimal runnable `app.py` that reproduces this demo (real Hedron, not the docs simulator):

    ```python title="app.py"
    import os

    from hedron import ComponentRef, Hedron, Page, Poll, html, swap

    app = Hedron(
        title="Poll demo",
        security="standard",
        explorer="off",
        session_secret=os.environ.get("HEDRON_SESSION_SECRET", "dev-only"),
    )

    box = app.region("poll-box")
    ref = ComponentRef(
        logical_id="job-42",
        path="/jobs/42",
        target=box.selector,
        swap="innerHTML",
    )

    _STEPS = [
        ("Queued", "Waiting for a worker"),
        ("Running", "Step 1 of 2"),
        ("Running", "Step 2 of 2"),
        ("Complete", "84 records imported; polling stopped"),
    ]
    _tick = 0


    def panel(state: str, detail: str):
        return html.div(
            html.strong(state),
            html.span(detail),
            id=box.id,
            role="status",
        )


    @app.page("/")
    def home() -> Page:
        return Page(
            Poll(
                ref=ref,
                interval_ms=700,
                target_id=box.id,
                content=panel(*_STEPS[0]),
            ),
            title="Poll",
        )


    @app.view("/jobs/42", fragment_regions=(box,))
    def tick():
        global _tick
        state, detail = _STEPS[min(_tick, len(_STEPS) - 1)]
        _tick = min(_tick + 1, len(_STEPS) - 1)
        return swap(panel(state, detail))
    ```


## Basic use

```python
from hedron import Poll, Status

component = Poll(ref=ComponentRef('job-status', job_id=job.id), interval_ms=2000, content=Status('Queued'))
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

HTMX's `every Nms` trigger refreshes the component into its collision-free self-target. Repeated instances can share one ComponentRef safely. Stop polling by returning replacement markup without the polling attributes once the terminal state is reached.

This component can initiate or represent a backend interaction. The live documentation intercepts that interaction with JavaScript and shows the same pending, success, or replacement states without making a real request. In an application, keep the URL, authorization, validation, and returned fragment on the server; JavaScript is only progressive enhancement.

## Constructor and parameters

```python
Poll(*, ref, interval_ms=5000, target_id=None, content=None)
```

| Parameter | Type | Meaning |
|---|---|---|
| `ref` | `ComponentRef` | Typed polling endpoint. |
| `interval_ms` | `int` | Interval, clamped to at least 250 ms. |
| `target_id` | `str | None` | Explicit self-target ID; generated collision-free by default. |
| `content` | `NodeLike | None` | Initial content. |

## Composition and backend behavior

Keep `Poll` at the smallest semantic boundary. Fragment routes should return only
the replaced region and preserve stable target IDs across success, validation, empty,
loading, and error responses.

Mutating flows must use POST, validate CSRF, authorize on the server, re-validate typed input, and return a bounded fragment. GET remains safe and repeatable; native submit should still work without HTMX.

## Accessibility

Announce only meaningful state transitions; announcing every timer tick overwhelms screen-reader users.

## Security

Escaping and `SafeUrl` / `TrustedHtml` are framework concerns; authorization and data
exposure remain application code. Redact secrets before rendering.

## Common mistakes

- Use conservative intervals, private caching where appropriate, and a terminal response that stops server load.
- Do not copy docs-preview JavaScript into an application server.

## Testing

```python
from hedron import RenderMode, render

result = render(component, mode=RenderMode.FRAGMENT)
assert result.html
assert not result.diagnostics
```

[All component demos](index.md) · [Built-in API](../api/BUILT_INS.md) · [Testing](../guides/testing.md)

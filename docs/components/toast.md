---
title: Toast
description: Render a polite, transient-looking status message.
---

# `Toast`

Render a polite, transient-looking status message.

| | |
|---|---|
| Import | `from hedron import Toast` |
| Distribution | `hedron` |
| Backend activity | No |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

=== "Demo"

    Docs simulation — not a running Hedron server. Interactive demos show a “Simulated HTMX” trace when applicable.

    <!-- hedron-sim:component-toast -->

=== "Code"

    Minimal runnable `app.py` that reproduces this demo (real Hedron, not the docs simulator):

    ```python title="app.py"
    import os

    from hedron import Hedron, OobHost, Page, Stack, Toast, html, swap

    app = Hedron(
        title="Toast demo",
        security="standard",
        explorer="off",
        session_secret=os.environ.get("HEDRON_SESSION_SECRET", "dev-only"),
    )

    host = app.region("toast-host")


    @app.page("/")
    def home() -> Page:
        return Page(
            Stack(
                html.button(
                    "Copy API key",
                    type="button",
                    **{
                        "hx-post": "/copy-key",
                        "hx-target": host.selector,
                        "hx-swap": "innerHTML",
                    },
                ),
                OobHost(id=host.id),
            ),
            title="Toast",
        )


    @app.action("/copy-key", method="POST", fragment_regions=(host,))
    def copy():
        return swap(Toast("API key copied.", tone="success"))
    ```


## Basic use

```python
from hedron import Toast
component = Toast('API key copied.', tone='success')
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

Toast emits a polite status region with a tone class and optional TTL. Pair with ToastHost at frozen `#hedron-toast`. Danger toasts stay until dismissed unless `ttl_ms` is set; they render a Dismiss control (`data-hedron-toast-dismiss`) handled by `hedron-ui.mjs`.

This component can initiate or represent a backend interaction. The live documentation intercepts that interaction with JavaScript and shows the same pending, success, or replacement states without making a real request. In an application, keep the URL, authorization, validation, and returned fragment on the server; JavaScript is only progressive enhancement.

## Constructor and parameters

```text
Toast(message, *, tone='info', ttl_ms=4000)
```

| Parameter | Type | Meaning |
|---|---|---|
| `message` | `str` | Escaped toast text. |
| `tone` | `info | success | warning | danger` | Visual token. |
| `ttl_ms` | `int | None` | Auto-dismiss delay in milliseconds; danger defaults to none. |

## Composition and backend behavior

Keep `Toast` at the smallest semantic boundary. Fragment routes should return only
the replaced region and preserve stable target IDs across success, validation, empty,
loading, and error responses.

Mutating flows must use POST, validate CSRF, authorize on the server, re-validate typed input, and return a bounded fragment. GET remains safe and repeatable; native submit should still work without HTMX.

## Accessibility

If application JavaScript removes the toast, allow enough reading time, pause any timer on hover or focus, and preserve critical messages elsewhere.

## Security

Escaping and `SafeUrl` / `TrustedHtml` are framework concerns; authorization and data
exposure remain application code. Redact secrets before rendering.

## Common mistakes

- Never auto-dismiss errors that require a user decision, and do not expect a `dismissible` constructor option.
- Do not copy docs-preview JavaScript into an application server.

## Testing

```python
from hedron import RenderMode, render

result = render(component, mode=RenderMode.FRAGMENT)
assert result.html
assert not result.diagnostics
```

[All component demos](index.md) · [Built-in API](../api/BUILT_INS.md) · [Testing](../guides/testing.md)

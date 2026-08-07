---
title: AttrHost
description: Stable element that can receive attribute-only OOB updates.
---

# `AttrHost`

Stable element that can receive attribute-only OOB updates.

| | |
|---|---|
| Import | `from hedron import AttrHost` |
| Distribution | `hedron` |
| Backend activity | No |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

=== "Demo"

    Docs simulation — not a running Hedron server. Interactive demos show a “Simulated HTMX” trace when applicable.

    <!-- hedron-sim:component-attr-host -->

=== "Code"

    Minimal runnable `app.py` that reproduces this demo (real Hedron, not the docs simulator):

    ```python title="app.py"
    import os

    from hedron import AttrHost, Hedron, Page, Stack, html, swap

    app = Hedron(
        title="AttrHost demo",
        security="standard",
        explorer="off",
        session_secret=os.environ.get("HEDRON_SESSION_SECRET", "dev-only"),
    )

    host = app.region("demo-attr-host")


    def host_node(state: str):
        return AttrHost(
            html.strong("Attr host"),
            html.small(f"data-state={state}"),
            id=host.id,
            attrs={"data-state": state},
        )


    @app.page("/")
    def home() -> Page:
        return Page(
            Stack(
                host_node("idle"),
                html.button(
                    "Run attribute update",
                    type="button",
                    **{
                        "hx-get": "/status-attrs",
                        "hx-target": host.selector,
                        "hx-swap": "outerHTML",
                    },
                ),
            ),
            title="AttrHost",
        )


    @app.fragment("/status-attrs", region=host)
    def attrs():
        return swap(host_node("ready"))
    ```


## Basic use

```python
from hedron import AttrHost, Text

component = AttrHost(Text('Ready'), id='status-host', attrs={'data-state': 'idle'})
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

AttrHost is the companion to OobHost for attribute swaps (for example busy/disabled flags) without replacing the whole subtree.

This component can initiate or represent a backend interaction. The live documentation intercepts that interaction with JavaScript and shows the same pending, success, or replacement states without making a real request. In an application, keep the URL, authorization, validation, and returned fragment on the server; JavaScript is only progressive enhancement.

## Constructor and parameters

```python
AttrHost(*nodes, *, id, tag='div', attrs=None, class_=None)
```

| Parameter | Type | Meaning |
|---|---|---|
| `id` | `str` | Required stable element id. |
| `attrs` | `mapping | None` | Initial attributes eligible for attr OOB patches. |
| `tag / class_` | `str` | Host element and optional classes. |

## Composition and backend behavior

Keep `AttrHost` at the smallest semantic boundary. Fragment routes should return only
the replaced region and preserve stable target IDs across success, validation, empty,
loading, and error responses.

Mutating flows must use POST, validate CSRF, authorize on the server, re-validate typed input, and return a bounded fragment. GET remains safe and repeatable; native submit should still work without HTMX.

## Accessibility

Keep attribute names on an allowlist and authorize updates the same way as content OOB.

## Security

Escaping and `SafeUrl` / `TrustedHtml` are framework concerns; authorization and data
exposure remain application code. Redact secrets before rendering.

## Common mistakes

- Do not treat AttrHost as a general DOM mutation API.
- Do not copy docs-preview JavaScript into an application server.

## Testing

```python
from hedron import RenderMode, render

result = render(component, mode=RenderMode.FRAGMENT)
assert result.html
assert not result.diagnostics
```

[All component demos](index.md) · [Built-in API](../api/BUILT_INS.md) · [Testing](../guides/testing.md)

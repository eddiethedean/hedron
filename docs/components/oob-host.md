---
title: OobHost
description: Stable out-of-band swap root with a reserved id.
---

# `OobHost`

Stable out-of-band swap root with a reserved id.

| | |
|---|---|
| Import | `from hedron import OobHost` |
| Distribution | `hedron` |
| Backend activity | No |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

=== "Demo"

    Docs simulation — not a running Hedron server. Interactive demos show a “Simulated HTMX” trace when applicable.

    <!-- hedron-sim:component-oob-host -->

=== "Code"

    Minimal runnable `app.py` that reproduces this demo (real Hedron, not the docs simulator):

    ```python title="app.py"
    import os

    from hedron import (
        Hedron,
        InteractionResult,
        OobHost,
        OobUpdate,
        Page,
        Stack,
        html,
    )
    from hedron_core.interaction import InteractionPolicy

    app = Hedron(
        title="OobHost demo",
        security="standard",
        explorer="off",
        session_secret=os.environ.get("HEDRON_SESSION_SECRET", "dev-only"),
    )

    main = app.region("oob-primary")
    host = app.region("demo-oob-host")


    def primary(*, draft: bool = True):
        return html.div(
            html.strong("Draft profile" if draft else "Profile saved"),
            html.span("Primary region waiting for save." if draft else "Primary region updated."),
            id=main.id,
        )


    @app.page("/")
    def home() -> Page:
        return Page(
            Stack(
                primary(draft=True),
                OobHost(
                    html.span("OOB host"),
                    html.span(html.strong("#status"), html.small("Stable swap root")),
                    id=host.id,
                ),
                html.button(
                    "Save",
                    type="button",
                    **{
                        "hx-post": "/profile",
                        "hx-target": main.selector,
                        "hx-swap": "outerHTML",
                    },
                ),
            ),
            title="OobHost",
        )


    @app.component("/profile", methods=["POST"], fragment_regions=(main, host))
    def save() -> InteractionResult:
        return InteractionResult(
            content=primary(draft=False),
            region_id=main.id,
            oob=(
                OobUpdate(
                    content=OobHost(
                        html.span("Saved"),
                        html.span(html.strong("#status"), html.small("Out-of-band update")),
                        id=host.id,
                    ),
                    element_id=host.id,
                ),
            ),
            policy=InteractionPolicy(declared_regions=(main, host)),
        )
    ```


## Basic use

```python
from hedron import OobHost, Toast

component = OobHost(Toast('Saved'), id='toast-host')
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

OobHost reserves a predictable DOM root for `oob_swap` updates. Pair with authorize_oob_update and reserved-id rules so fragments cannot target arbitrary selectors.

This component can initiate or represent a backend interaction. The live documentation intercepts that interaction with JavaScript and shows the same pending, success, or replacement states without making a real request. In an application, keep the URL, authorization, validation, and returned fragment on the server; JavaScript is only progressive enhancement.

## Constructor and parameters

```python
OobHost(*nodes, *, id, tag='div', class_=None)
```

| Parameter | Type | Meaning |
|---|---|---|
| `id` | `str` | Required stable element id for OOB targeting. |
| `tag` | `str` | Host element tag (default div). |
| `class_` | `str | None` | Optional CSS classes. |

## Composition and backend behavior

Keep `OobHost` at the smallest semantic boundary. Fragment routes should return only
the replaced region and preserve stable target IDs across success, validation, empty,
loading, and error responses.

Mutating flows must use POST, validate CSRF, authorize on the server, re-validate typed input, and return a bounded fragment. GET remains safe and repeatable; native submit should still work without HTMX.

## Accessibility

Give each OOB host a unique page-local id and keep toast/status regions outside MainPanel when they must survive panel swaps.

## Security

Escaping and `SafeUrl` / `TrustedHtml` are framework concerns; authorization and data
exposure remain application code. Redact secrets before rendering.

## Common mistakes

- Do not reuse an OobHost id for ordinary fragment regions.
- Do not copy docs-preview JavaScript into an application server.

## Testing

```python
from hedron import RenderMode, render

result = render(component, mode=RenderMode.FRAGMENT)
assert result.html
assert not result.diagnostics
```

[All component demos](index.md) · [Built-in API](../api/BUILT_INS.md) · [Testing](../guides/testing.md)

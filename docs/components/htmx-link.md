---
title: HtmxLink
description: Navigate with a SafeUrl href and typed HTMX attributes for in-shell swaps.
---

# `HtmxLink`

Navigate with a SafeUrl href and typed HTMX attributes for in-shell swaps.

| | |
|---|---|
| Import | `from hedron import HtmxLink` |
| Distribution | `hedron` |
| Backend activity | No |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

=== "Demo"

    Docs simulation — not a running Hedron server. Interactive demos show a “Simulated HTMX” trace when applicable.

    <!-- hedron-sim:component-htmx-link -->

=== "Code"

    Minimal runnable `app.py` that reproduces this demo (real Hedron, not the docs simulator):

    ```python title="app.py"
    import os

    from hedron import Fragment, Hedron, HtmxLink, MainPanel, Page, Stack, html, swap

    app = Hedron(
        title="HtmxLink demo",
        security="standard",
        explorer="off",
        session_secret=os.environ.get("HEDRON_SESSION_SECRET", "dev-only"),
    )

    panel = app.region("htmx-link-panel")


    @app.page("/")
    def home() -> Page:
        return Page(
            Stack(
                html.div(
                    HtmxLink("Reports", "/reports", target=panel.selector, swap="innerHTML"),
                    HtmxLink("Team", "/team", target=panel.selector, swap="innerHTML"),
                ),
                MainPanel(
                    html.strong("Choose a link"),
                    html.span("HtmxLink keeps href as the progressive-enhancement path."),
                    id=panel.id,
                ),
            ),
            title="HtmxLink",
        )


    @app.fragment("/reports", region=panel)
    def reports():
        return swap(
            Fragment(
                html.strong("Reports"),
                html.span("In-shell navigation with SafeUrl href fallback."),
            )
        )


    @app.fragment("/team", region=panel)
    def team():
        return swap(
            Fragment(
                html.strong("Team"),
                html.span("Ordinary href still works without JavaScript."),
            )
        )
    ```


## Basic use

```python
from hedron import HtmxLink

component = HtmxLink('Reports', '/reports', hx_get='/reports', hx_target='#main-panel', hx_swap='innerHTML')
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

HtmxLink keeps ordinary anchor navigation as the progressive-enhancement path while attaching the same HTMX allowlist used by `html.a` and ComponentRef. Use it under Nav for in-shell panel swaps.

This component can initiate or represent a backend interaction. The live documentation intercepts that interaction with JavaScript and shows the same pending, success, or replacement states without making a real request. In an application, keep the URL, authorization, validation, and returned fragment on the server; JavaScript is only progressive enhancement.

## Constructor and parameters

```python
HtmxLink(label, href, *, hx_get=None, hx_target=None, hx_swap=None, active=False, class_=None)
```

| Parameter | Type | Meaning |
|---|---|---|
| `label` | `str` | Visible link text. |
| `href` | `SafeUrl | str` | Validated navigation URL (also the no-JS fallback). |
| `hx_get / hx_post / …` | `str | None` | Typed HTMX request attrs from the html.a allowlist. |
| `hx_target / hx_swap` | `str | None` | Approved swap target and strategy. |
| `active` | `bool` | Optional active styling hook for current location. |
| `class_` | `str | None` | Additional CSS classes. |

## Composition and backend behavior

Keep `HtmxLink` at the smallest semantic boundary. Fragment routes should return only
the replaced region and preserve stable target IDs across success, validation, empty,
loading, and error responses.

Mutating flows must use POST, validate CSRF, authorize on the server, re-validate typed input, and return a bounded fragment. GET remains safe and repeatable; native submit should still work without HTMX.

## Accessibility

Prefer descriptive labels and stable region ids for `hx_target`. Keep CSRF and region authorization on the receiving action.

## Security

Escaping and `SafeUrl` / `TrustedHtml` are framework concerns; authorization and data
exposure remain application code. Redact secrets before rendering.

## Common mistakes

- Do not use HtmxLink for mutating form posts that belong on Button or Form; it is navigation-first.
- Do not copy docs-preview JavaScript into an application server.

## Testing

```python
from hedron import RenderMode, render

result = render(component, mode=RenderMode.FRAGMENT)
assert result.html
assert not result.diagnostics
```

[All component demos](index.md) · [Built-in API](../api/BUILT_INS.md) · [Testing](../guides/testing.md)

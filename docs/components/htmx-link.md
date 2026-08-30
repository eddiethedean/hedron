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


    @app.view("/reports", fragment_regions=(panel,))
    def reports():
        return swap(
            Fragment(
                html.strong("Reports"),
                html.span("In-shell navigation with SafeUrl href fallback."),
            )
        )


    @app.view("/team", fragment_regions=(panel,))
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
component = HtmxLink('Reports', '/reports', target='#main-panel', swap='innerHTML', select='#main-panel')
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

HtmxLink keeps ordinary anchor navigation as the progressive-enhancement path while attaching typed HTMX attrs. `select` / `select_oob` pull nodes from the response; server `OobUpdate` emits `hx-swap-oob` envelopes. Use one OOB mechanism per target—prefer explicit `OobUpdate(..., swap='innerHTML')` and omit matching `select_oob` so semantic shell hosts (for example `<nav aria-label=...>`) keep their tag and accessible name.

This component can initiate or represent a backend interaction. The live documentation intercepts that interaction with JavaScript and shows the same pending, success, or replacement states without making a real request. In an application, keep the URL, authorization, validation, and returned fragment on the server; JavaScript is only progressive enhancement.

## Constructor and parameters

```text
HtmxLink(label, href, *, method='get', target=None, swap='outerHTML', select=None, select_oob=None, push_url=False, preload=None, active=False, attrs=None, class_=None)
```

| Parameter | Type | Meaning |
|---|---|---|
| `label` | `str` | Visible link text. |
| `href` | `SafeUrl | str` | Validated navigation URL (also the no-JS fallback). |
| `method` | `str` | HTMX verb mapped to hx-get / hx-post / … (default get). |
| `target / swap` | `str | None` | Approved hx-target and hx-swap for the primary region. |
| `select` | `str | None` | Optional hx-select for the primary fragment in the response. |
| `select_oob` | `str | None` | Optional hx-select-oob for response nodes that should be treated as OOB. Do not combine with a server OobUpdate for the same id. |
| `push_url` | `bool | str` | Optional hx-push-url for in-shell history. |
| `preload` | `str | None` | Optional GET-only HTMX preload initiation: mousedown, mouseover, or touchstart. Registers the preload extension; never a compatibility default. |
| `active` | `bool` | Optional active styling hook for current location. |
| `attrs` | `dict[str, object] | None` | Safe passthrough limited to `title`, `data-*`, and `aria-*`; URL, HTMX, style, and event attributes are rejected. |
| `class_` | `str | None` | Additional CSS classes. |

## Composition and backend behavior

Keep `HtmxLink` at the smallest semantic boundary. Fragment routes should return only
the replaced region and preserve stable target IDs across success, validation, empty,
loading, and error responses.

Mutating flows must use POST, validate CSRF, authorize on the server, re-validate typed input, and return a bounded fragment. GET remains safe and repeatable; native submit should still work without HTMX.

## Accessibility

Prefer descriptive labels and stable region ids for `target`. Keep CSRF and region authorization on the receiving action.

## Security

Escaping and `SafeUrl` / `TrustedHtml` are framework concerns; authorization and data
exposure remain application code. Redact secrets before rendering.

## Common mistakes

- Do not set `select_oob` for an id that the same navigation flow also updates via `OobUpdate`—that combination can replace landmark hosts with Hedron's OOB wrapper. Do not use HtmxLink for mutating form posts that belong on Button or Form; it is navigation-first.
- Do not copy docs-preview JavaScript into an application server.

## Testing

```python
from hedron import RenderMode, render

result = render(component, mode=RenderMode.FRAGMENT)
assert result.html
assert not result.diagnostics
```

[All component demos](index.md) · [Built-in API](../api/BUILT_INS.md) · [Testing](../guides/testing.md)

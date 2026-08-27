---
title: MainPanel
description: Primary HTMX swap region for AppShell document/fragment dual paths.
---

# `MainPanel`

Primary HTMX swap region for AppShell document/fragment dual paths.

| | |
|---|---|
| Import | `from hedron import MainPanel` |
| Distribution | `hedron` |
| Backend activity | No |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

=== "Demo"

    Docs simulation — not a running Hedron server. Interactive demos show a “Simulated HTMX” trace when applicable.

    <!-- hedron-sim:component-main-panel -->

=== "Code"

    Minimal runnable `app.py` that reproduces this demo (real Hedron, not the docs simulator):

    ```python title="app.py"
    import os

    from hedron import AppShell, Hedron, Nav, NavLink, Page, html, swap

    app = Hedron(
        title="AppShell demo",
        security="standard",
        explorer="off",
        session_secret=os.environ.get("HEDRON_SESSION_SECRET", "dev-only"),
    )

    panel = app.region("comp-main-panel")


    def panel_body(name: str, detail: str):
        return html.div(html.strong(name), html.span(detail))


    @app.page("/")
    def home() -> Page:
        return Page(
            AppShell(
                nav=Nav(
                    NavLink("Home", "/home", target=panel.selector, swap="innerHTML", active=True),
                    NavLink("Reports", "/reports", target=panel.selector, swap="innerHTML"),
                    NavLink("Settings", "/settings", target=panel.selector, swap="innerHTML"),
                ),
                body=panel_body("Home", "Overview metrics stay in MainPanel."),
                panel_id=panel.id,
            ),
            title="AppShell",
        )


    @app.view("/home", fragment_regions=(panel,))
    def home_frag():
        return swap(panel_body("Home", "Overview metrics stay in MainPanel."))


    @app.view("/reports", fragment_regions=(panel,))
    def reports_frag():
        return swap(panel_body("Reports", "Reports fragment swapped into the panel."))


    @app.view("/settings", fragment_regions=(panel,))
    def settings_frag():
        return swap(panel_body("Settings", "Settings fragment; side nav stays put."))
    ```


## Basic use

```python
from hedron import Heading, MainPanel, Text

component = MainPanel(Heading('Dashboard', level=1), Text('Overview'), id='main-panel')
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

MainPanel is the body region AppShell composes for full-document and fragment responses. Keep navigable content here so shell chrome remains stable across swaps.

This component can initiate or represent a backend interaction. The live documentation intercepts that interaction with JavaScript and shows the same pending, success, or replacement states without making a real request. In an application, keep the URL, authorization, validation, and returned fragment on the server; JavaScript is only progressive enhancement.

## Constructor and parameters

```python
MainPanel(*nodes, *, id='main-panel', class_=None)
```

| Parameter | Type | Meaning |
|---|---|---|
| `id` | `str` | Stable region id targeted by NavLink/HtmxLink swaps. |
| `class_` | `str | None` | Optional CSS classes. |

## Composition and backend behavior

Keep `MainPanel` at the smallest semantic boundary. Fragment routes should return only
the replaced region and preserve stable target IDs across success, validation, empty,
loading, and error responses.

Mutating flows must use POST, validate CSRF, authorize on the server, re-validate typed input, and return a bounded fragment. GET remains safe and repeatable; native submit should still work without HTMX.

## Accessibility

Authorize the panel id in fragment_regions / InteractionPolicy for HTMX targets.

## Security

Escaping and `SafeUrl` / `TrustedHtml` are framework concerns; authorization and data
exposure remain application code. Redact secrets before rendering.

## Common mistakes

- Do not nest multiple competing main panels on one page.
- Do not copy docs-preview JavaScript into an application server.

## Testing

```python
from hedron import RenderMode, render

result = render(component, mode=RenderMode.FRAGMENT)
assert result.html
assert not result.diagnostics
```

[All component demos](index.md) · [Built-in API](../api/BUILT_INS.md) · [Testing](../guides/testing.md)

---
title: Pagination
description: Render crawlable page links that optionally swap a target through HTMX.
---

# `Pagination`

Render crawlable page links that optionally swap a target through HTMX.

| | |
|---|---|
| Import | `from hedron import Pagination` |
| Distribution | `hedron` |
| Backend activity | On navigation |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

=== "Demo"

    Docs simulation — not a running Hedron server. Interactive demos show a “Simulated HTMX” trace when applicable.

    <!-- hedron-sim:component-pagination -->

=== "Code"

    Minimal runnable `app.py` that reproduces this demo (real Hedron, not the docs simulator):

    ```python title="app.py"
    import os

    from fastapi import Request

    from hedron import Hedron, Page, Pagination, Stack, html, swap

    app = Hedron(
        title="Pagination demo",
        security="standard",
        explorer="off",
        session_secret=os.environ.get("HEDRON_SESSION_SECRET", "dev-only"),
    )

    results = app.region("page-results")
    PAGES = {
        1: ("Results 1–3", "Alpha · Bravo · Charlie"),
        2: ("Results 4–6", "Delta · Echo · Foxtrot"),
        3: ("Results 7–9", "Golf · Hotel · India"),
    }


    def panel(page: int):
        title, detail = PAGES[page]
        return html.div(html.strong(title), html.span(detail), id=results.id)


    @app.page("/")
    def home() -> Page:
        return Page(
            Stack(
                panel(1),
                Pagination(
                    page=1,
                    page_size=3,
                    total=9,
                    base_path="/results",
                    target=results.selector,
                ),
            ),
            title="Pagination",
        )


    @app.view("/results", fragment_regions=(results,))
    def page_frag(request: Request):
        page = int(request.query_params.get("page", "1"))
        page = page if page in PAGES else 1
        return swap(panel(page))
    ```


## Basic use

```python
from hedron import Pagination

component = Pagination(page=2, page_size=25, total=93, base_path='/audit', target='#audit-table')
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

Every page is a real safe anchor, so navigation works without HTMX. With a target, each link adds a GET request and innerHTML swap. Current-page context is included in the accessible label.

This component can initiate or represent a backend interaction. The live documentation intercepts that interaction with JavaScript and shows the same pending, success, or replacement states without making a real request. In an application, keep the URL, authorization, validation, and returned fragment on the server; JavaScript is only progressive enhancement.

## Constructor and parameters

```python
Pagination(*, page, page_size, total, base_path, target=None)
```

| Parameter | Type | Meaning |
|---|---|---|
| `page` | `int` | Current one-based page. |
| `page_size` | `int` | Rows per page. |
| `total` | `int` | Total result count. |
| `base_path` | `str` | Safe base URL, with or without query parameters. |
| `target` | `safe CSS selector | None` | Optional HTMX target. |

## Composition and backend behavior

Keep `Pagination` at the smallest semantic boundary. Fragment routes should return only
the replaced region and preserve stable target IDs across success, validation, empty,
loading, and error responses.

Mutating flows must use POST, validate CSRF, authorize on the server, re-validate typed input, and return a bounded fragment. GET remains safe and repeatable; native submit should still work without HTMX.

## Accessibility

Preserve focus and announce the new result range after a fragment swap.

## Security

Escaping and `SafeUrl` / `TrustedHtml` are framework concerns; authorization and data
exposure remain application code. Redact secrets before rendering.

## Common mistakes

- The server remains authoritative for out-of-range pages and must preserve filters in generated URLs.
- Do not copy docs-preview JavaScript into an application server.

## Testing

```python
from hedron import RenderMode, render

result = render(component, mode=RenderMode.FRAGMENT)
assert result.html
assert not result.diagnostics
```

[All component demos](index.md) · [Built-in API](../api/BUILT_INS.md) · [Testing](../guides/testing.md)

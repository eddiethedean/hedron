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

<!-- hedron-sim:component-pagination -->

The preview is a local docs simulation (not a running Hedron server). Interactive demos show a “Simulated HTMX” trace when applicable.

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

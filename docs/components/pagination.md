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

<section class="hedron-component-demo" data-hedron-component-demo="Pagination"><div class="hdc-stage"><div class="hdc-result" data-hdc-page-content><strong>Results 1–3</strong><span>Alpha · Bravo · Charlie</span></div><nav class="hdc-pages" aria-label="Demo pagination"><a href="?page=1" aria-current="page" data-hdc-page="1">1</a><a href="?page=2" data-hdc-page="2">2</a><a href="?page=3" data-hdc-page="3">3</a></nav></div><div class="hdc-request" data-hdc-request hidden><span>Simulated HTMX</span><code>GET /fragment → 200</code></div></section>

The preview is intentionally small enough to inspect with a keyboard and screen reader. It demonstrates the component's semantic result, not a screenshot. If the example represents HTMX activity, the “Simulated HTMX” trace confirms that documentation JavaScript supplied the response locally.

## Basic use

```python
from hedron import Pagination

component = Pagination(page=2, page_size=25, total=93, base_path='/audit', target='#audit-table')
```

In a route, return the component inside a `Page`, or return it directly as a fragment through the framework adapter. Components are immutable descriptions of output: construct the complete state on the server and let the renderer serialize it.

## How it works

Every page is a real safe anchor, so navigation works without HTMX. With a target, each link adds a GET request and innerHTML swap. Current-page context is included in the accessible label.

This component can initiate or represent a backend interaction. The live documentation intercepts that interaction with JavaScript and shows the same pending, success, or replacement states without making a real request. In an application, keep the URL, authorization, validation, and returned fragment on the server; JavaScript is only progressive enhancement.

The component participates in Hedron's normal escaping, URL, and attribute validation. Values are data unless an API explicitly requires `SafeUrl` or reviewed `TrustedHtml`; do not pre-escape strings and do not concatenate HTML.

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

Keyword defaults are chosen for a safe, progressively enhanced baseline. Pass stable IDs when another component, a label, a URL fragment, a test, or an HTMX target must address the rendered node. Prefer typed component composition over hand-built HTML strings.

## Composition and backend behavior

Use `Pagination` at the smallest level that owns its semantics. Page routes normally compose it under `Page`, `Main`, and an explicit heading structure. HTMX fragment routes should return only the region being replaced and keep stable target IDs across success, validation, empty, loading, and error responses.

Mutating flows must use POST, validate CSRF, authorize on the server, re-validate typed input, and return a bounded fragment. GET remains safe and repeatable; native submit should still work without HTMX.

## Accessibility

Preserve focus and announce the new result range after a fragment swap.

Verify keyboard use, visible focus, zoom, and reduced motion for interactive states. Prefer native semantics and status/alert announcements over color-only cues.

## Security and validation

Escape and trust-boundary types (`SafeUrl`, `TrustedHtml`) remain framework concerns; authorization and data exposure remain yours. Redact secrets before rendering.

## Common mistakes

- The server remains authoritative for out-of-range pages and must preserve filters in generated URLs.
- Do not copy docs-preview JavaScript into an application server; demos simulate HTMX locally.
- Choose components for semantics first, then theme them.

## Testing

```python
from hedron import RenderMode, render

result = render(component, mode=RenderMode.FRAGMENT)
assert result.html
assert not result.diagnostics
```

For interactive flows, assert method, URL, headers, fragment body, and status with a framework test client. Add a browser test when keyboard or HTMX swap behavior is material.

[All component demos](index.md) · [Built-in API baseline](../api/BUILT_INS.md) · [Testing UI](../guides/testing.md) · [Forms and actions](../guides/forms-and-actions.md)

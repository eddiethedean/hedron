---
title: Table
description: Render a small static data table with explicit headers.
---

# `Table`

Render a small static data table with explicit headers.

| | |
|---|---|
| Import | `from hedron import Table` |
| Distribution | `hedron` |
| Backend activity | No |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

<section class="hedron-component-demo" data-hedron-component-demo="Table"><div class="hdc-stage"><table class="hdc-table"><caption>Service health</caption><thead><tr><th>Service</th><th>Status</th></tr></thead><tbody><tr><td><strong>API</strong></td><td><span class="hdc-badge hdc-success">Healthy</span></td></tr><tr><td><strong>Worker</strong></td><td><span class="hdc-badge hdc-success">Healthy</span></td></tr></tbody></table></div></section>

The preview is a local docs simulation (not a running Hedron server). Interactive demos show a “Simulated HTMX” trace when applicable.

## Basic use

```python
from hedron import Status, Table

component = Table(['Service', 'Status'], [['API', 'Healthy'], ['Worker', 'Healthy']], caption='Service health')
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

The component emits a native table, optional caption, a header row using column-scoped header cells, and a body. It is intentionally static; use DataTable for paging and larger datasets.

This component's core behavior is server-rendered HTML and does not require a browser runtime. The preview is ordinary semantic HTML, so keyboard, form, link, and disclosure behavior comes from the platform.

## Constructor and parameters

```python
Table(headers, rows, *, caption=None)
```

| Parameter | Type | Meaning |
|---|---|---|
| `headers` | `Sequence[str]` | Column headings. |
| `rows` | `Sequence[Sequence[NodeLike]]` | Rows matching the header count. |
| `caption` | `str | None` | Accessible table name and context. |

## Composition and backend behavior

Keep `Table` at the smallest semantic boundary. Fragment routes should return only
the replaced region and preserve stable target IDs across success, validation, empty,
loading, and error responses.

This component is primarily presentational; keep any mutation on an explicit action or component route.

## Accessibility

Add a concise caption when surrounding prose does not already identify the table.

## Security

Escaping and `SafeUrl` / `TrustedHtml` are framework concerns; authorization and data
exposure remain application code. Redact secrets before rendering.

## Common mistakes

- Keep every row the same width as the headers; do not use a table only for visual alignment.
- Do not copy docs-preview JavaScript into an application server.

## Testing

```python
from hedron import RenderMode, render

result = render(component, mode=RenderMode.FRAGMENT)
assert result.html
assert not result.diagnostics
```

[All component demos](index.md) · [Built-in API](../api/BUILT_INS.md) · [Testing](../guides/testing.md)

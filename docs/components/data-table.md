---
title: DataTable
description: Render typed or pre-fetched rows as an accessible bounded data table.
---

# `DataTable`

Render typed or pre-fetched rows as an accessible bounded data table.

| | |
|---|---|
| Import | `from hedron import DataTable` |
| Distribution | `hedron[data]` |
| Backend activity | No |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

<section class="hedron-component-demo" data-hedron-component-demo="DataTable"><div class="hdc-stage"><div class="hdc-table-toolbar"><span><strong>Team directory</strong><small>Current workspace members</small></span><label class="hdc-filter">Filter employees<input type="search" placeholder="Search by name or team" data-hdc-filter></label></div><table class="hdc-table"><caption class="hdc-visually-hidden">Employees</caption><thead><tr><th>Name</th><th>Team</th><th>Status</th></tr></thead><tbody data-hdc-rows><tr><td><strong>Ada</strong></td><td>Platform</td><td><span class="hdc-badge hdc-success">Active</span></td></tr><tr><td><strong>Grace</strong></td><td>Compiler</td><td><span class="hdc-badge hdc-success">Active</span></td></tr><tr><td><strong>Alan</strong></td><td>Research</td><td><span class="hdc-badge hdc-warning">Leave</span></td></tr></tbody></table><p class="hdc-muted" role="status" data-hdc-status>Showing 3 employees.</p></div></section>

The preview is intentionally small enough to inspect with a keyboard and screen reader. It demonstrates the component's semantic result, not a screenshot. If the example represents HTMX activity, the “Simulated HTMX” trace confirms that documentation JavaScript supplied the response locally.

Install the optional provider before importing this component:

```bash
pip install "hedron[data]"
```

## Basic use

```python
from hedron import DataTable

component = DataTable(rows, row_model=EmployeeRow, caption='Employees', page_size=25)
```

In a route, return the component inside a `Page`, or return it directly as a fragment through the framework adapter. Components are immutable descriptions of output: construct the complete state on the server and let the renderer serialize it.

## How it works

DataTable normalizes mappings and models, resolves visible columns, redacts protected values, emits native table semantics, and exposes a CSV helper that omits hidden and secret columns. It does not fetch a source itself; fetch remote data first and pass a bounded DataPage.

This component's core behavior is server-rendered HTML and does not require a browser runtime. The preview is ordinary semantic HTML, so keyboard, form, link, and disclosure behavior comes from the platform.

The component participates in Hedron's normal escaping, URL, and attribute validation. Values are data unless an API explicitly requires `SafeUrl` or reviewed `TrustedHtml`; do not pre-escape strings and do not concatenate HTML.

## Constructor and parameters

```python
DataTable(rows=None, *, row_model=None, columns=None, page=None, query=None, caption=None, empty_message='No rows', page_size=25, allow_download=False)
```

| Parameter | Type | Meaning |
|---|---|---|
| `rows` | `Any` | Materialized mappings or model rows. |
| `row_model` | `type[Model] | None` | Typed column source. |
| `columns` | `Sequence[Column] | None` | Explicit column configuration. |
| `page` | `DataPage | None` | Pre-fetched bounded page with total and version metadata. |
| `query` | `DataQuery | None` | Query metadata associated with the rows. |
| `caption` | `str | None` | Accessible table name. |
| `empty_message` | `str` | Text spanning the empty table body. |
| `page_size` | `int` | Page-size metadata. |
| `allow_download` | `bool` | Expose download intent to the owning application. |

Keyword defaults are chosen for a safe, progressively enhanced baseline. Pass stable IDs when another component, a label, a URL fragment, a test, or an HTMX target must address the rendered node. Prefer typed component composition over hand-built HTML strings.

## Composition and backend behavior

Use `DataTable` at the smallest level that owns its semantics. Page routes normally compose it under `Page`, `Main`, and an explicit heading structure. HTMX routes should return only the component region being replaced and should preserve stable target IDs across success, validation, empty, loading, and error responses.

When a request can mutate data, use POST, validate CSRF, authenticate and authorize on the server, validate typed input again, and return a bounded fragment. GET interactions must remain safe and repeatable. Native links and forms should still reach a useful server response when HTMX is unavailable.

## Accessibility

Use a precise caption, human column labels, and text equivalents for status or icon cells.

Test the demo and your application with keyboard-only input, visible focus, zoom, reduced motion, and at least one screen reader. Never make color, position, animation, or an icon the only carrier of state. Dynamic results need an appropriate status or alert and a deliberate focus strategy.

## Security and validation

Treat all request data, database content, filenames, URLs, labels, chart data, and Markdown as untrusted until the owning boundary validates it. Hedron escapes text and constrains dangerous surfaces, but it cannot decide application authorization or data exposure. Keep responses bounded, redact secrets before rendering, and use the narrowest URL and trust types available.

## Common mistakes

- Do not render an unbounded query or assume `allow_download` creates an authorized download route.
- Do not copy the demo's JavaScript into a server application as a substitute for an HTMX endpoint. The simulation exists only because the hosted docs have no application backend.
- Do not select components by visual appearance alone; choose the native semantics first, then theme them.

## Testing

Render the component at the boundary you intend to ship and assert behavior rather than a large, brittle snapshot:

```python
from hedron import RenderMode, render

result = render(component, mode=RenderMode.FRAGMENT)
assert result.html
assert not result.diagnostics
```

For interactive use, add a framework test that sends the same method, URL, headers, and typed payload as the browser, then assert the returned fragment, status code, cache policy, and security headers. Add a browser test for keyboard behavior, focus, live announcements, and the HTMX swap lifecycle when those behaviors are material.

[All component demos](index.md) · [Built-in API baseline](../api/BUILT_INS.md) · [Testing UI](../guides/testing.md)

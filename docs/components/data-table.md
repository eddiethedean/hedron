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

Use `DataTable` at the smallest level that owns its semantics. Page routes normally compose it under `Page`, `Main`, and an explicit heading structure. HTMX fragment routes should return only the region being replaced and keep stable target IDs across success, validation, empty, loading, and error responses.

This component is primarily presentational; keep any mutation on an explicit action or component route.

## Accessibility

Use a precise caption, human column labels, and text equivalents for status or icon cells.

Verify keyboard use, visible focus, zoom, and reduced motion for interactive states. Prefer native semantics and status/alert announcements over color-only cues.

## Security and validation

Escape and trust-boundary types (`SafeUrl`, `TrustedHtml`) remain framework concerns; authorization and data exposure remain yours. Redact secrets before rendering.

## Common mistakes

- Do not render an unbounded query or assume `allow_download` creates an authorized download route.
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

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

The preview is a local docs simulation (not a running Hedron server). Interactive demos show a “Simulated HTMX” trace when applicable.

Install the optional provider before importing this component:

```bash
pip install "hedron[data]>=0.61.0,<0.62"
```

## Basic use

```python
from hedron import DataTable

component = DataTable(rows, row_model=EmployeeRow, caption='Employees', page_size=25)
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

DataTable normalizes mappings and models, resolves visible columns, redacts protected values, emits native table semantics, and exposes a CSV helper that omits hidden and secret columns. It does not fetch a source itself; fetch remote data first and pass a bounded DataPage.

This component's core behavior is server-rendered HTML and does not require a browser runtime. The preview is ordinary semantic HTML, so keyboard, form, link, and disclosure behavior comes from the platform.

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

## Composition and backend behavior

Keep `DataTable` at the smallest semantic boundary. Fragment routes should return only
the replaced region and preserve stable target IDs across success, validation, empty,
loading, and error responses.

`DataTable` renders data the server already prepared. Keep queries, authorization, and redaction on the route or data source — do not treat the component as a place for side effects.

## Accessibility

Use a precise caption, human column labels, and text equivalents for status or icon cells.

## Security

Escaping and `SafeUrl` / `TrustedHtml` are framework concerns; authorization and data
exposure remain application code. Redact secrets before rendering.

## Common mistakes

- Do not render an unbounded query or assume `allow_download` creates an authorized download route.
- Do not copy docs-preview JavaScript into an application server.

## Testing

```python
from hedron import RenderMode, render

result = render(component, mode=RenderMode.FRAGMENT)
assert result.html
assert not result.diagnostics
```

[All component demos](index.md) · [Built-in API](../api/BUILT_INS.md) · [Testing](../guides/testing.md)

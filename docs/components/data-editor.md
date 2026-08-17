---
title: DataEditor
description: Edit bounded typed rows and submit explicit change sets.
---

# `DataEditor`

Edit bounded typed rows and submit explicit change sets.

| | |
|---|---|
| Import | `from hedron import DataEditor` |
| Distribution | `hedron[data]` |
| Backend activity | On save |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

<section class="hedron-component-demo" data-hedron-component-demo="DataEditor"><div class="hdc-stage"><table class="hdc-editor"><caption>Editable allocation</caption><thead><tr><th>Name</th><th>Allocation</th></tr></thead><tbody><tr><td>Ada</td><td><input type="number" min="0" max="100" value="80" aria-label="Ada allocation" data-hdc-dirty></td></tr><tr><td>Grace</td><td><input type="number" min="0" max="100" value="60" aria-label="Grace allocation" data-hdc-dirty></td></tr></tbody></table><button class="hdc-button hdc-primary" type="button" data-hdc-action="save-editor">Save changes</button><p role="status" data-hdc-status>No unsaved changes.</p></div><div class="hdc-request" data-hdc-request hidden><span>Simulated HTMX</span><code>GET /fragment → 200</code></div></section>

The preview is a local docs simulation (not a running Hedron server). Interactive demos show a “Simulated HTMX” trace when applicable.

Install the optional provider before importing this component:

```bash
pip install "hedron[data]>=0.48.0,<0.49"
```

## Basic use

```python
from hedron import DataEditor

component = DataEditor(rows, key='allocation-editor', row_model=EmployeeRow, on_save=save_changes, key_field='id', allow_deletes=False)
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

The editor tracks updates, additions, and deletions as a typed DataChanges payload, filters changes against writable-field policy, and applies them through a callback or data source. The browser asset improves editing, but server-side policy remains authoritative.

This component can initiate or represent a backend interaction. The live documentation intercepts that interaction with JavaScript and shows the same pending, success, or replacement states without making a real request. In an application, keep the URL, authorization, validation, and returned fragment on the server; JavaScript is only progressive enhancement.

## Constructor and parameters

```python
DataEditor(rows=None, *, key='editor', row_model=None, columns=None, key_field='id', on_save=None, source=None, page=None, save_mode='batch', page_size=25, caption=None, save_endpoint=None, allow_deletes=True)
```

| Parameter | Type | Meaning |
|---|---|---|
| `rows` | `Any` | Materialized editable rows. |
| `key` | `str` | Stable browser editor identity. |
| `row_model / columns` | `schema inputs` | Field types and edit policy. |
| `key_field` | `str` | Stable row identity field. |
| `on_save` | `callable | None` | Validated change-set handler. |
| `source / page` | `data inputs` | Sync source or explicit bounded page. |
| `save_mode` | `SaveMode` | Batch or supported save behavior. |
| `page_size` | `int` | Source fetch bound. |
| `caption` | `str | None` | Accessible editor/table name. |
| `save_endpoint` | `str | None` | Browser module submission endpoint. |
| `allow_deletes` | `bool` | Permit delete change sets; defaults to true. |

## Composition and backend behavior

Keep `DataEditor` at the smallest semantic boundary. Fragment routes should return only
the replaced region and preserve stable target IDs across success, validation, empty,
loading, and error responses.

Mutating flows must use POST, validate CSRF, authorize on the server, re-validate typed input, and return a bounded fragment. GET remains safe and repeatable; native submit should still work without HTMX.

## Accessibility

Maintain keyboard editing, visible focus, field-level errors, and a clear saved or conflicted status.

## Security

Escaping and `SafeUrl` / `TrustedHtml` are framework concerns; authorization and data
exposure remain application code. Redact secrets before rendering.

## Common mistakes

- Set `allow_deletes=False` unless deletion is intentional, and never trust client change sets, hidden fields, or optimistic versions without server validation.
- Do not copy docs-preview JavaScript into an application server.

## Testing

```python
from hedron import RenderMode, render

result = render(component, mode=RenderMode.FRAGMENT)
assert result.html
assert not result.diagnostics
```

[All component demos](index.md) · [Built-in API](../api/BUILT_INS.md) · [Testing](../guides/testing.md)

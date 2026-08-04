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

The preview is intentionally small enough to inspect with a keyboard and screen reader. It demonstrates the component's semantic result, not a screenshot. If the example represents HTMX activity, the “Simulated HTMX” trace confirms that documentation JavaScript supplied the response locally.

Install the optional provider before importing this component:

```bash
pip install "hedron[data]"
```

## Basic use

```python
from hedron import DataEditor

component = DataEditor(rows, key='allocation-editor', row_model=EmployeeRow, on_save=save_changes, key_field='id', allow_deletes=False)
```

In a route, return the component inside a `Page`, or return it directly as a fragment through the framework adapter. Components are immutable descriptions of output: construct the complete state on the server and let the renderer serialize it.

## How it works

The editor tracks updates, additions, and deletions as a typed DataChanges payload, filters changes against writable-field policy, and applies them through a callback or data source. The browser asset improves editing, but server-side policy remains authoritative.

This component can initiate or represent a backend interaction. The live documentation intercepts that interaction with JavaScript and shows the same pending, success, or replacement states without making a real request. In an application, keep the URL, authorization, validation, and returned fragment on the server; JavaScript is only progressive enhancement.

The component participates in Hedron's normal escaping, URL, and attribute validation. Values are data unless an API explicitly requires `SafeUrl` or reviewed `TrustedHtml`; do not pre-escape strings and do not concatenate HTML.

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

Keyword defaults are chosen for a safe, progressively enhanced baseline. Pass stable IDs when another component, a label, a URL fragment, a test, or an HTMX target must address the rendered node. Prefer typed component composition over hand-built HTML strings.

## Composition and backend behavior

Use `DataEditor` at the smallest level that owns its semantics. Page routes normally compose it under `Page`, `Main`, and an explicit heading structure. HTMX routes should return only the component region being replaced and should preserve stable target IDs across success, validation, empty, loading, and error responses.

When a request can mutate data, use POST, validate CSRF, authenticate and authorize on the server, validate typed input again, and return a bounded fragment. GET interactions must remain safe and repeatable. Native links and forms should still reach a useful server response when HTMX is unavailable.

## Accessibility

Maintain keyboard editing, visible focus, field-level errors, and a clear saved or conflicted status.

Test the demo and your application with keyboard-only input, visible focus, zoom, reduced motion, and at least one screen reader. Never make color, position, animation, or an icon the only carrier of state. Dynamic results need an appropriate status or alert and a deliberate focus strategy.

## Security and validation

Treat all request data, database content, filenames, URLs, labels, chart data, and Markdown as untrusted until the owning boundary validates it. Hedron escapes text and constrains dangerous surfaces, but it cannot decide application authorization or data exposure. Keep responses bounded, redact secrets before rendering, and use the narrowest URL and trust types available.

## Common mistakes

- Set `allow_deletes=False` unless deletion is intentional, and never trust client change sets, hidden fields, or optimistic versions without server validation.
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

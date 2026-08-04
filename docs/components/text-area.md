---
title: TextArea
description: Collect multi-line plain text.
---

# `TextArea`

Collect multi-line plain text.

| | |
|---|---|
| Import | `from hedron import TextArea` |
| Distribution | `hedron` |
| Backend activity | No |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

<section class="hedron-component-demo" data-hedron-component-demo="TextArea"><div class="hdc-stage"><div class="hdc-form"><label for="demo-notes">Deployment notes</label><textarea id="demo-notes" rows="4" placeholder="Add context…"></textarea></div></div></section>

The preview is a local docs simulation (not a running Hedron server). Interactive demos show a “Simulated HTMX” trace when applicable.

## Basic use

```python
from hedron import TextArea

component = TextArea('notes', rows=6, placeholder='Add deployment context…')
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

The value is rendered as escaped text content, not as an HTML value attribute. Browsers retain native selection, resizing, and keyboard behavior.

This component's core behavior is server-rendered HTML and does not require a browser runtime. The preview is ordinary semantic HTML, so keyboard, form, link, and disclosure behavior comes from the platform.

## Constructor and parameters

```python
TextArea(name, *, id=None, value='', rows=4, required=False, placeholder=None)
```

| Parameter | Type | Meaning |
|---|---|---|
| `name` | `str` | Submitted field name. |
| `id` | `str | None` | Control ID. |
| `value` | `str` | Text between the textarea tags. |
| `rows` | `int` | Initial visible row count. |
| `required` | `bool` | Native required constraint. |
| `placeholder` | `str | None` | Optional example or hint. |

## Composition and backend behavior

Keep `TextArea` at the smallest semantic boundary. Fragment routes should return only
the replaced region and preserve stable target IDs across success, validation, empty,
loading, and error responses.

This component is primarily presentational; keep any mutation on an explicit action or component route.

## Accessibility

Use a visible label and explain format or length expectations before the control.

## Security

Escaping and `SafeUrl` / `TrustedHtml` are framework concerns; authorization and data
exposure remain application code. Redact secrets before rendering.

## Common mistakes

- Do not accept rich HTML through TextArea without a separate sanitization and trust pipeline.
- Do not copy docs-preview JavaScript into an application server.

## Testing

```python
from hedron import RenderMode, render

result = render(component, mode=RenderMode.FRAGMENT)
assert result.html
assert not result.diagnostics
```

[All component demos](index.md) · [Built-in API](../api/BUILT_INS.md) · [Testing](../guides/testing.md)

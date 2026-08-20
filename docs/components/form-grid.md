---
title: FormGrid
description: Responsive field grid for forms and settings panels.
---

# `FormGrid`

Responsive field grid for forms and settings panels.

| | |
|---|---|
| Import | `from hedron import FormGrid` |
| Distribution | `hedron` |
| Backend activity | No |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

<section class="hedron-component-demo" data-hedron-component-demo="FormGrid"><div class="hdc-stage"><div class="hdc-grid"><div class="hdc-form"><label for="demo-fg-name">Name</label><input id="demo-fg-name" type="text" value="Ada"></div><div class="hdc-form"><label for="demo-fg-email">Email</label><input id="demo-fg-email" type="email" value="ada@example.com"></div></div></div></section>

The preview is a local docs simulation (not a running Hedron server). Interactive demos show a “Simulated HTMX” trace when applicable.

## Basic use

```python
from hedron import FormField, FormGrid, TextInput

component = FormGrid(FormField('Name', TextInput(name='name')), FormField('Email', TextInput(name='email')))
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

FormGrid lays out labelled controls with theme-owned gutters and collapse behavior.

This component's core behavior is server-rendered HTML and does not require a browser runtime. The preview is ordinary semantic HTML, so keyboard, form, link, and disclosure behavior comes from the platform.

## Constructor and parameters

```python
FormGrid(*fields, *, columns=2, collapse='md', gap='1rem', id=None, class_=None)
```

| Parameter | Type | Meaning |
|---|---|---|
| `fields` | `NodeLike` | Form fields or labelled controls. |
| `columns` | `int | Mapping` | Column count or responsive map. |
| `collapse` | `str` | Breakpoint where the grid stacks. |

## Composition and backend behavior

Keep `FormGrid` at the smallest semantic boundary. Fragment routes should return only
the replaced region and preserve stable target IDs across success, validation, empty,
loading, and error responses.

`FormGrid` is primarily presentational; keep any mutation on an explicit action or component route.

## Accessibility

Keep related fields in one FormGrid; use Stack for vertical-only sections.

## Security

Escaping and `SafeUrl` / `TrustedHtml` are framework concerns; authorization and data
exposure remain application code. Redact secrets before rendering.

## Common mistakes

- Do not mix FormGrid with equal-column Grid when you need ratio control—use SplitView.
- Do not copy docs-preview JavaScript into an application server.

## Testing

```python
from hedron import RenderMode, render

result = render(component, mode=RenderMode.FRAGMENT)
assert result.html
assert not result.diagnostics
```

[All component demos](index.md) · [Built-in API](../api/BUILT_INS.md) · [Testing](../guides/testing.md)

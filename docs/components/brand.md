---
title: Brand
description: Product mark for AppShell chrome without application CSS.
---

# `Brand`

Product mark for AppShell chrome without application CSS.

| | |
|---|---|
| Import | `from hedron import Brand` |
| Distribution | `hedron` |
| Backend activity | No |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

<section class="hedron-component-demo" data-hedron-component-demo="Brand"><div class="hdc-stage"><div class="hdc-inline"><strong>Hedron</strong><span class="hdc-muted">Brand mark</span></div></div></section>

The preview is a local docs simulation (not a running Hedron server). Interactive demos show a “Simulated HTMX” trace when applicable.

## Basic use

```python
from hedron import Brand

component = Brand('Hedron', href='/')
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

Brand emits a typed chrome mark with first-party presentation markers.

This component's core behavior is server-rendered HTML and does not require a browser runtime. The preview is ordinary semantic HTML, so keyboard, form, link, and disclosure behavior comes from the platform.

## Constructor and parameters

```python
Brand(name, *, href=None, mark=None, id=None, class_=None)
```

| Parameter | Type | Meaning |
|---|---|---|
| `name` | `str` | Product or workspace name. |
| `href` | `SafeUrl | str | None` | Optional home navigation target. |
| `mark` | `NodeLike | None` | Optional logo/mark slot. |

## Composition and backend behavior

Keep `Brand` at the smallest semantic boundary. Fragment routes should return only
the replaced region and preserve stable target IDs across success, validation, empty,
loading, and error responses.

`Brand` is primarily presentational; keep any mutation on an explicit action or component route.

## Accessibility

Keep brand text readable when an image mark is present.

## Security

Escaping and `SafeUrl` / `TrustedHtml` are framework concerns; authorization and data
exposure remain application code. Redact secrets before rendering.

## Common mistakes

- Do not style Brand with application CSS; use presentation tokens.
- Do not copy docs-preview JavaScript into an application server.

## Testing

```python
from hedron import RenderMode, render

result = render(component, mode=RenderMode.FRAGMENT)
assert result.html
assert not result.diagnostics
```

[All component demos](index.md) · [Built-in API](../api/BUILT_INS.md) · [Testing](../guides/testing.md)

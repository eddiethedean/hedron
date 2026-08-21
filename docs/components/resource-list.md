---
title: ResourceList
description: List resources with first-party density and presentation tokens.
---

# `ResourceList`

List resources with first-party density and presentation tokens.

| | |
|---|---|
| Import | `from hedron import ResourceList` |
| Distribution | `hedron` |
| Backend activity | No |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

<section class="hedron-component-demo" data-hedron-component-demo="ResourceList"><div class="hdc-stage"><div class="hdc-stack"><span><b>Orders</b><small>Open work</small></span><span><b>Sites</b><small>Ready</small></span></div></div></section>

The preview is a local docs simulation (not a running Hedron server). Interactive demos show a “Simulated HTMX” trace when applicable.

## Basic use

```python
from hedron import ResourceList, ResourceRow

component = ResourceList(ResourceRow('Orders', description='Open work', href='/orders'), density='compact')
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

ResourceList is the zero-application-CSS list surface for navigable collections.

This component's core behavior is server-rendered HTML and does not require a browser runtime. The preview is ordinary semantic HTML, so keyboard, form, link, and disclosure behavior comes from the platform.

## Constructor and parameters

```python
ResourceList(*rows, *, density=None, id=None, class_=None)
```

| Parameter | Type | Meaning |
|---|---|---|
| `rows` | `ResourceRow | NodeLike` | Resource rows or compatible children. |
| `density` | `comfortable | compact | None` | Optional density token. |

## Composition and backend behavior

Keep `ResourceList` at the smallest semantic boundary. Fragment routes should return only
the replaced region and preserve stable target IDs across success, validation, empty,
loading, and error responses.

`ResourceList` renders data the server already prepared. Keep queries, authorization, and redaction on the route or data source — do not treat the component as a place for side effects.

## Accessibility

Prefer ResourceRow children so title/description/actions stay structured.

## Security

Escaping and `SafeUrl` / `TrustedHtml` are framework concerns; authorization and data
exposure remain application code. Redact secrets before rendering.

## Common mistakes

- Do not nest a full interactive form inside every row.
- Do not copy docs-preview JavaScript into an application server.

## Testing

```python
from hedron import RenderMode, render

result = render(component, mode=RenderMode.FRAGMENT)
assert result.html
assert not result.diagnostics
```

[All component demos](index.md) · [Built-in API](../api/BUILT_INS.md) · [Testing](../guides/testing.md)

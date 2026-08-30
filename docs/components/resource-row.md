---
title: ResourceRow
description: One resource entry with optional link, meta, and actions.
---

# `ResourceRow`

One resource entry with optional link, meta, and actions.

| | |
|---|---|
| Import | `from hedron import ResourceRow` |
| Distribution | `hedron` |
| Backend activity | No |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

<section class="hedron-component-demo" data-hedron-component-demo="ResourceRow"><div class="hdc-stage"><div class="hdc-stack"><span><b>North warehouse</b><small>Ready</small></span></div></div></section>

The preview is a local docs simulation (not a running Hedron server). Interactive demos show a “Simulated HTMX” trace when applicable.

## Basic use

```python
from hedron import ResourceRow
component = ResourceRow('North warehouse', description='Ready', href='/sites/north')
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

ResourceRow keeps title/description structured and avoids nested interactive targets.

This component's core behavior is server-rendered HTML and does not require a browser runtime. The preview is ordinary semantic HTML, so keyboard, form, link, and disclosure behavior comes from the platform.

## Constructor and parameters

```text
ResourceRow(title, *, description=None, href=None, actions=None, meta=None, density=None)
```

| Parameter | Type | Meaning |
|---|---|---|
| `title` | `str` | Primary resource label. |
| `description` | `str | None` | Supporting text. |
| `href` | `SafeUrl | str | None` | Primary navigation target. |
| `actions` | `NodeLike | None` | Trailing action slot when not using href. |
| `meta` | `NodeLike | None` | Secondary metadata slot. |

## Composition and backend behavior

Keep `ResourceRow` at the smallest semantic boundary. Fragment routes should return only
the replaced region and preserve stable target IDs across success, validation, empty,
loading, and error responses.

`ResourceRow` renders data the server already prepared. Keep queries, authorization, and redaction on the route or data source — do not treat the component as a place for side effects.

## Accessibility

Use either a primary href or an actions slot—not both competing click targets.

## Security

Escaping and `SafeUrl` / `TrustedHtml` are framework concerns; authorization and data
exposure remain application code. Redact secrets before rendering.

## Common mistakes

- Do not put a button inside a row that is already a link.
- Do not copy docs-preview JavaScript into an application server.

## Testing

```python
from hedron import RenderMode, render

result = render(component, mode=RenderMode.FRAGMENT)
assert result.html
assert not result.diagnostics
```

[All component demos](index.md) · [Built-in API](../api/BUILT_INS.md) · [Testing](../guides/testing.md)

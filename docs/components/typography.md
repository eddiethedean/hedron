---
title: Typography
description: Role-first text helper bound to the type scale.
---

# `Typography`

Role-first text helper bound to the type scale.

| | |
|---|---|
| Import | `from hedron import Typography` |
| Distribution | `hedron` |
| Backend activity | No |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

<section class="hedron-component-demo" data-hedron-component-demo="Typography"><div class="hdc-stage"><div class="hdc-type"><span class="hdc-eyebrow">Title role</span><p><strong>Release readiness</strong></p><span class="hdc-muted">Body role · supporting copy on the type scale.</span></div></div></section>

The preview is a local docs simulation (not a running Hedron server). Interactive demos show a “Simulated HTMX” trace when applicable.

## Basic use

```python
from hedron import Typography
component = Typography('Release readiness', role='title')
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

Typography maps author intent (role) to theme CSS classes without requiring application type CSS.

This component's core behavior is server-rendered HTML and does not require a browser runtime. The preview is ordinary semantic HTML, so keyboard, form, link, and disclosure behavior comes from the platform.

## Constructor and parameters

```text
Typography(content, *, role='body', as_='p', class_=None)
```

| Parameter | Type | Meaning |
|---|---|---|
| `content` | `str` | Escaped text content. |
| `role` | `str` | Closed typography role from the theme scale. |
| `as_` | `p | span | div | strong | em | small | code` | Native element to emit. |

## Composition and backend behavior

Keep `Typography` at the smallest semantic boundary. Fragment routes should return only
the replaced region and preserve stable target IDs across success, validation, empty,
loading, and error responses.

`Typography` is primarily presentational; keep any mutation on an explicit action or component route.

## Accessibility

Use Heading for document outline levels; use Typography for scale-driven body, caption, and title text.

## Security

Escaping and `SafeUrl` / `TrustedHtml` are framework concerns; authorization and data
exposure remain application code. Redact secrets before rendering.

## Common mistakes

- Do not invent CSS font sizes for product chrome—pick a role.
- Do not copy docs-preview JavaScript into an application server.

## Testing

```python
from hedron import RenderMode, render

result = render(component, mode=RenderMode.FRAGMENT)
assert result.html
assert not result.diagnostics
```

[All component demos](index.md) · [Built-in API](../api/BUILT_INS.md) · [Testing](../guides/testing.md)

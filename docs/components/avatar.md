---
title: Avatar
description: Person or entity avatar with image or initials fallback.
---

# `Avatar`

Person or entity avatar with image or initials fallback.

| | |
|---|---|
| Import | `from hedron import Avatar` |
| Distribution | `hedron` |
| Backend activity | No |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

<section class="hedron-component-demo" data-hedron-component-demo="Avatar"><div class="hdc-stage"><div class="hdc-inline"><span class="hdc-badge" aria-label="Ada Lovelace">AL</span></div></div></section>

The preview is a local docs simulation (not a running Hedron server). Interactive demos show a “Simulated HTMX” trace when applicable.

## Basic use

```python
from hedron import Avatar
component = Avatar('Ada Lovelace', size='md')
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

Avatar falls back to initials when no image is provided.

This component's core behavior is server-rendered HTML and does not require a browser runtime. The preview is ordinary semantic HTML, so keyboard, form, link, and disclosure behavior comes from the platform.

## Constructor and parameters

```text
Avatar(name, *, src=None, size=None, appearance=None, shape='circle')
```

| Parameter | Type | Meaning |
|---|---|---|
| `name` | `str` | Accessible name and initials source. |
| `src` | `SafeUrl | str | None` | Optional image URL. |
| `size` | `sm | md | lg | None` | Named size token. |
| `appearance` | `plain | raised | None` | Optional appearance token. |
| `shape` | `circle | rounded | square` | Avatar shape token. |

## Composition and backend behavior

Keep `Avatar` at the smallest semantic boundary. Fragment routes should return only
the replaced region and preserve stable target IDs across success, validation, empty,
loading, and error responses.

`Avatar` is primarily presentational; keep any mutation on an explicit action or component route.

## Accessibility

Always supply a real name so the accessible label and initials are meaningful.

## Security

Escaping and `SafeUrl` / `TrustedHtml` are framework concerns; authorization and data
exposure remain application code. Redact secrets before rendering.

## Common mistakes

- Do not use decorative-only avatars without a name.
- Do not copy docs-preview JavaScript into an application server.

## Testing

```python
from hedron import RenderMode, render

result = render(component, mode=RenderMode.FRAGMENT)
assert result.html
assert not result.diagnostics
```

[All component demos](index.md) · [Built-in API](../api/BUILT_INS.md) · [Testing](../guides/testing.md)

---
title: StyleScope
description: Bound a subtree to theme, finite variant, color mode, and density markers only.
---

# `StyleScope`

Bound a subtree to theme, finite variant, color mode, and density markers only.

| | |
|---|---|
| Import | `from hedron import StyleScope` |
| Distribution | `hedron` |
| Backend activity | No |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

<section class="hedron-component-demo" data-hedron-component-demo="StyleScope"><div class="hdc-stage"><div class="hdc-container" data-hedron-style-scope="true" data-hedron-theme="aurora" data-hedron-color-mode="dark" data-hedron-density="compact"><strong>Scoped panel</strong><p class="hdc-muted">Theme, color mode, and density markers only.</p></div></div></section>

The preview is a local docs simulation (not a running Hedron server). Interactive demos show a “Simulated HTMX” trace when applicable.

## Basic use

```python
from hedron import StyleScope, Text
component = StyleScope(Text('Scoped panel'), theme='aurora', variant='dense', color_mode='dark', density='compact')
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

StyleScope is a visible boundary for theme, finite variant, color mode, density, and presentation mappings. Use `presentation={'PageHeader.title': 'display', 'Heading': 'section-heading'}` to provide nearest-scope recipe defaults; explicit component settings remain authoritative.

This component's core behavior is server-rendered HTML and does not require a browser runtime. The preview is ordinary semantic HTML, so keyboard, form, link, and disclosure behavior comes from the platform.

## Constructor and parameters

```text
StyleScope(*nodes, *, theme=None, color_mode=None, density=None, variant=None, presentation=None, recipes=(), id=None, class_=None, mark=None)
```

| Parameter | Type | Meaning |
|---|---|---|
| `nodes` | `NodeLike` | StyleScope body content. |
| `theme` | `str | None` | Optional registered theme name emitted as `data-hedron-theme`. |
| `variant` | `str | None` | Optional finite registered variant emitted as `data-hedron-variant`. Unknown names fail closed. |
| `color_mode` | `light | dark | None` | Optional color-mode marker (`data-hedron-color-mode`). |
| `density` | `compact | comfortable | spacious | None` | Optional density marker (`data-hedron-density`). |
| `presentation` | `dict[str, str] | None` | Finite slot-to-recipe defaults inherited by descendants. |
| `recipes` | `Sequence[StyleRecipe]` | Optional scoped recipe catalog used to resolve presentation names into bounded component markers. |

## Composition and backend behavior

Keep `StyleScope` at the smallest semantic boundary. Fragment routes should return only
the replaced region and preserve stable target IDs across success, validation, empty,
loading, and error responses.

`StyleScope` is primarily presentational; keep any mutation on an explicit action or component route.

## Accessibility

Prefer StyleScope when a region must override theme, finite variant, color mode, or density without application CSS.

## Security

Escaping and `SafeUrl` / `TrustedHtml` are framework concerns; authorization and data
exposure remain application code. Redact secrets before rendering.

## Common mistakes

- Do not pass arbitrary CSS or unresolved selectors; use finite StyleRecipe values and documented presentation slots.
- Do not copy docs-preview JavaScript into an application server.

## Testing

```python
from hedron import RenderMode, render

result = render(component, mode=RenderMode.FRAGMENT)
assert result.html
assert not result.diagnostics
```

[All component demos](index.md) · [Built-in API](../api/BUILT_INS.md) · [Testing](../guides/testing.md)

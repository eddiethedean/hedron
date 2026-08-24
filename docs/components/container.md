---
title: Container
description: Constrain and center a readable block of page content.
---

# `Container`

Constrain and center a readable block of page content.

| | |
|---|---|
| Import | `from hedron import Container` |
| Distribution | `hedron` |
| Backend activity | No |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

<section class="hedron-component-demo" data-hedron-component-demo="Container"><div class="hdc-stage"><div class="hdc-container"><span class="hdc-eyebrow">Account settings</span><h3>Profile</h3><p>This readable block stays centered with a bounded width.</p><a href="#component-demo-result">Edit profile →</a></div></div></section>

The preview is a local docs simulation (not a running Hedron server). Interactive demos show a “Simulated HTMX” trace when applicable.

## Basic use

```python
from hedron import Container, Heading, Text

component = Container(Heading('Profile', level=1), Text('Manage your public details.'), query='inline-size', name='profile')
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

The component emits an addressable div and always retains the `hedron-container` theme hook. In 0.59, `query='inline-size'` opts the boundary into container-aware responsive styling and `name=` adds a validated named-container marker. Positional nodes and `children=` use the same normalization rules, and an application class augments rather than disables the built-in layout. Width, gutters, and breakpoints remain theme CSS concerns.

Phase 0.61 adds finite width, alignment, and spacing markers without changing the default
viewport behavior. These tokens are theme hooks, not arbitrary CSS values.

This component's core behavior is server-rendered HTML and does not require a browser runtime. The preview is ordinary semantic HTML, so keyboard, form, link, and disclosure behavior comes from the platform.

## Constructor and parameters

```python
Container(*nodes, children=None, id=None, class_=None, query='none', name=None,
          max_width=None, align=None, padding=None)
```

| Parameter | Type | Meaning |
|---|---|---|
| `nodes` | `NodeLike` | Positional content inside the width constraint. |
| `children` | `NodeLike | sequence | None` | Keyword alternative for generated or declarative child lists; combines with positional nodes. |
| `id` | `str | None` | Stable DOM target for links, tests, and HTMX swaps. |
| `class_` | `str | None` | Application class appended after `hedron-container`; the built-in theme hook is retained. |
| `query` | `Literal['none', 'inline-size']` | Opt into an inline-size query boundary. Default: `'none'` (existing viewport behavior). |
| `name` | `str | None` | Validated container name, valid only with `query='inline-size'`. |
| `max_width` | `'xs' | 'sm' | 'md' | 'lg' | 'xl' | 'full' | None` | Finite readable-width token. |
| `align` | `'start' | 'center' | 'end' | None` | Inline alignment inside the containing block. |
| `padding` | `str | None` | Theme spacing token such as `sm`, `md`, or `lg`. |

## Composition and backend behavior

Keep `Container` at the smallest semantic boundary. Fragment routes should return only
the replaced region and preserve stable target IDs across success, validation, empty,
loading, and error responses.

`Container` is primarily presentational; keep any mutation on an explicit action or component route.

## Accessibility

A container has no semantics of its own, so keep headings and landmarks inside it.

## Security

Escaping and `SafeUrl` / `TrustedHtml` are framework concerns; authorization and data
exposure remain application code. Redact secrets before rendering.

## Common mistakes

- Do not use Container as a substitute for Main or Section. Do not assume `query='inline-size'` is a viewport breakpoint; use the existing responsive maps when viewport semantics are intended.
- Do not copy docs-preview JavaScript into an application server.

## Testing

```python
from hedron import RenderMode, render

result = render(component, mode=RenderMode.FRAGMENT)
assert result.html
assert not result.diagnostics
```

[All component demos](index.md) · [Built-in API](../api/BUILT_INS.md) · [Testing](../guides/testing.md)

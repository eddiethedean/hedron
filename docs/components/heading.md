---
title: Heading
description: Create an explicit heading level without inferring document hierarchy.
---

# `Heading`

Create an explicit heading level without inferring document hierarchy.

| | |
|---|---|
| Import | `from hedron import Heading` |
| Distribution | `hedron` |
| Backend activity | No |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

<section class="hedron-component-demo" data-hedron-component-demo="Heading"><div class="hdc-stage"><div class="hdc-type"><span class="hdc-eyebrow">Production</span><h2>Deployment history</h2><p>Heading level two introduces this section.</p></div></div></section>

The preview is a local docs simulation (not a running Hedron server). Interactive demos show a “Simulated HTMX” trace when applicable.

## Basic use

```python
from hedron import Heading

component = Heading('Deployment history', level=2)
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

The requested level maps directly to `h1` through `h6`. Hedron does not guess levels because reusable components need their caller to own document structure.

This component's core behavior is server-rendered HTML and does not require a browser runtime. The preview is ordinary semantic HTML, so keyboard, form, link, and disclosure behavior comes from the platform.

## Constructor and parameters

```python
Heading(content='', *, level=2)
```

| Parameter | Type | Meaning |
|---|---|---|
| `content` | `str` | Escaped heading text. |
| `level` | `1 | 2 | 3 | 4 | 5 | 6` | Exact native heading level. |

## Composition and backend behavior

Keep `Heading` at the smallest semantic boundary. Fragment routes should return only
the replaced region and preserve stable target IDs across success, validation, empty,
loading, and error responses.

`Heading` is primarily presentational; keep any mutation on an explicit action or component route.

## Accessibility

Do not skip levels merely for appearance; style headings with CSS and preserve a logical outline.

## Security

Escaping and `SafeUrl` / `TrustedHtml` are framework concerns; authorization and data
exposure remain application code. Redact secrets before rendering.

## Common mistakes

- A page should generally have one descriptive level-one heading.
- Do not copy docs-preview JavaScript into an application server.

## Testing

```python
from hedron import RenderMode, render

result = render(component, mode=RenderMode.FRAGMENT)
assert result.html
assert not result.diagnostics
```

[All component demos](index.md) · [Built-in API](../api/BUILT_INS.md) · [Testing](../guides/testing.md)

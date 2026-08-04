---
title: Skeleton
description: Reserve space for content that is still loading.
---

# `Skeleton`

Reserve space for content that is still loading.

| | |
|---|---|
| Import | `from hedron import Skeleton` |
| Distribution | `hedron` |
| Backend activity | No |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

<section class="hedron-component-demo" data-hedron-component-demo="Skeleton"><div class="hdc-stage"><div aria-label="Loading preview"><span class="hdc-skeleton"></span><span class="hdc-skeleton"></span><span class="hdc-skeleton hdc-short"></span></div></div></section>

The preview is a local docs simulation (not a running Hedron server). Interactive demos show a “Simulated HTMX” trace when applicable.

## Basic use

```python
from hedron import Skeleton

component = Skeleton(lines=4)
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

Skeleton emits the requested placeholder lines, hides each line from the accessibility tree, and marks the wrapper busy. Pair it with a separate status message or the Loading component when users need progress context.

This component's core behavior is server-rendered HTML and does not require a browser runtime. The preview is ordinary semantic HTML, so keyboard, form, link, and disclosure behavior comes from the platform.

## Constructor and parameters

```python
Skeleton(*, lines=3)
```

| Parameter | Type | Meaning |
|---|---|---|
| `lines` | `int` | Number of presentation-only placeholder rows. |

## Composition and backend behavior

Keep `Skeleton` at the smallest semantic boundary. Fragment routes should return only
the replaced region and preserve stable target IDs across success, validation, empty,
loading, and error responses.

This component is primarily presentational; keep any mutation on an explicit action or component route.

## Accessibility

Because the visual lines are hidden semantically, provide an adjacent live status for meaningful waits.

## Security

Escaping and `SafeUrl` / `TrustedHtml` are framework concerns; authorization and data
exposure remain application code. Redact secrets before rendering.

## Common mistakes

- Validate `lines` in application configuration; zero or negative values produce an empty busy wrapper rather than a useful placeholder.
- Do not copy docs-preview JavaScript into an application server.

## Testing

```python
from hedron import RenderMode, render

result = render(component, mode=RenderMode.FRAGMENT)
assert result.html
assert not result.diagnostics
```

[All component demos](index.md) · [Built-in API](../api/BUILT_INS.md) · [Testing](../guides/testing.md)

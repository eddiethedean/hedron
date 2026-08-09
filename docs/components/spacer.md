---
title: Spacer
description: Semantic spacing primitive.
---

# `Spacer`

Semantic spacing primitive.

| | |
|---|---|
| Import | `from hedron import Spacer` |
| Distribution | `hedron` |
| Backend activity | No |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

<section class="hedron-component-demo" data-hedron-component-demo="Spacer"><div class="hdc-stage"><div class="hdc-stack"><span>Above</span><div style="height:1.5rem;border-left:2px dashed currentColor;opacity:0.35" aria-hidden="true"></div><span>Below</span></div></div></section>

The preview is a local docs simulation (not a running Hedron server). Interactive demos show a “Simulated HTMX” trace when applicable.

## Basic use

```python
from hedron import Spacer

component = Spacer(size='2rem')
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

Phase 0.15 surface. Prefer native HTML semantics and ordinary HTTP actions.

This component's core behavior is server-rendered HTML and does not require a browser runtime. The preview is ordinary semantic HTML, so keyboard, form, link, and disclosure behavior comes from the platform.

## Constructor and parameters

```python
Spacer(*, size: 'str' = '1rem', axis: "Literal['block', 'inline', 'both']" = 'block', id: 'str | None' = None, class_: 'str | None' = None, mark: 'str | None' = None, **kwargs: 'Any') -> 'None'
```

| Parameter | Type | Meaning |
|---|---|---|
| `size` | `str` | Spacer size (CSS length). Default: `'1rem'`. |
| `axis` | `Literal['block', 'inline', 'both']` | Spacer axis (`block`, `inline`, or `both`). Default: `'block'`. |
| `id` | `str | None` | Optional DOM `id`. Default: `None`. |
| `class_` | `str | None` | Optional CSS class string (`class` in HTML). Default: `None`. |
| `mark` | `str | None` | Optional stable test mark (`data-hedron-mark`). Default: `None`. |

## Composition and backend behavior

Keep `Spacer` at the smallest semantic boundary. Fragment routes should return only
the replaced region and preserve stable target IDs across success, validation, empty,
loading, and error responses.

`Spacer` is primarily presentational; keep any mutation on an explicit action or component route.

## Accessibility

Keyboard and screen-reader operable; no-JS fallback required where interactive.

## Security

Escaping and `SafeUrl` / `TrustedHtml` are framework concerns; authorization and data
exposure remain application code. Redact secrets before rendering.

## Common mistakes

- Do not treat client-only hints (geolocation, browser storage) as authorization.
- Do not copy docs-preview JavaScript into an application server.

## Testing

```python
from hedron import RenderMode, render

result = render(component, mode=RenderMode.FRAGMENT)
assert result.html
assert not result.diagnostics
```

[All component demos](index.md) · [Built-in API](../api/BUILT_INS.md) · [Testing](../guides/testing.md)

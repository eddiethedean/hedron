---
title: Popover
description: Native popover or details/summary disclosure.
---

# `Popover`

Native popover or details/summary disclosure.

| | |
|---|---|
| Import | `from hedron import Popover` |
| Distribution | `hedron` |
| Backend activity | No |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

<section class="hedron-component-demo" data-hedron-component-demo="Popover"><div class="hdc-stage"><button class="hdc-button" type="button" aria-expanded="false">Details</button><p class="hdc-muted">Popover content appears on activation in the live component.</p></div></section>

The preview is a local docs simulation (not a running Hedron server). Interactive demos show a “Simulated HTMX” trace when applicable.

## Basic use

```python
from hedron import Popover, Text

component = Popover('Info', Text('Details'))
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

Phase 0.15 surface. Prefer native HTML semantics and ordinary HTTP actions.

This component's core behavior is server-rendered HTML and does not require a browser runtime. The preview is ordinary semantic HTML, so keyboard, form, link, and disclosure behavior comes from the platform.

## Constructor and parameters

```python
Popover(*nodes: 'NodeLike', children: 'NodeLike' = None, label: 'str' = 'Open', mode: "Literal['popover', 'details']" = 'popover', placement: "Literal['block-start', 'block-end', 'inline-start', 'inline-end', 'center']" = 'block-end', collision: "Literal['flip', 'shift', 'static']" = 'flip', id: 'str | None' = None, class_: 'str | None' = None, mark: 'str | None' = None, **kwargs: 'Any') -> 'None'
```

| Parameter | Type | Meaning |
|---|---|---|
| `*nodes` | `NodeLike` | Positional child nodes. |
| `children` | `NodeLike` | Keyword alternative for child nodes; combines with positional children. Default: `None`. |
| `label` | `str` | Accessible label text shown to users. Default: `'Open'`. |
| `mode` | `Literal['popover', 'details']` | Presentation mode for the disclosure surface. Default: `'popover'`. |
| `placement` | `Literal['block-start', 'block-end', 'inline-start', 'inline-end', 'center']` | Layout placement for the dock. Default: `'block-end'`. |
| `collision` | `Literal['flip', 'shift', 'static']` | Constructor parameter. Default: `'flip'`. |
| `id` | `str | None` | Optional DOM `id`. Default: `None`. |
| `class_` | `str | None` | Optional CSS class string (`class` in HTML). Default: `None`. |
| `mark` | `str | None` | Optional stable test mark (`data-hedron-mark`). Default: `None`. |

## Composition and backend behavior

Keep `Popover` at the smallest semantic boundary. Fragment routes should return only
the replaced region and preserve stable target IDs across success, validation, empty,
loading, and error responses.

`Popover` is primarily presentational; keep any mutation on an explicit action or component route.

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

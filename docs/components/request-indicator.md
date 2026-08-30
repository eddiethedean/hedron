---
title: RequestIndicator
description: Polite HTMX busy indicator with theme-owned placement.
---

# `RequestIndicator`

Polite HTMX busy indicator with theme-owned placement.

| | |
|---|---|
| Import | `from hedron import RequestIndicator` |
| Distribution | `hedron` |
| Backend activity | No |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

<section class="hedron-component-demo" data-hedron-component-demo="RequestIndicator"><div class="hdc-stage"><div class="hdc-loading" role="status" aria-live="polite"><i></i><span>Saving…</span></div></div></section>

The preview is a local docs simulation (not a running Hedron server). Interactive demos show a “Simulated HTMX” trace when applicable.

## Basic use

```python
from hedron import RequestIndicator

component = RequestIndicator(label='Saving…', placement='top', id='save-indicator')
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

RequestIndicator carries HTMX's `htmx-indicator` class and a polite live region so busy state is never color-only.

This component's core behavior is server-rendered HTML and does not require a browser runtime. The preview is ordinary semantic HTML, so keyboard, form, link, and disclosure behavior comes from the platform.

## Constructor and parameters

```python
RequestIndicator(label='Loading…', *, placement='inline', visible_label=True, id=None, class_=None)
```

| Parameter | Type | Meaning |
|---|---|---|
| `label` | `str` | Busy-state text announced to assistive technology. |
| `placement` | `inline | top | bottom` | Closed placement vocabulary. |
| `visible_label` | `bool` | When false, keep the label visually hidden but announced. |

## Composition and backend behavior

Keep `RequestIndicator` at the smallest semantic boundary. Fragment routes should return only
the replaced region and preserve stable target IDs across success, validation, empty,
loading, and error responses.

`RequestIndicator` participates in interaction markup. Pair it with an explicit `@app.action` POST (and CSRF) when the control mutates state.

## Accessibility

Reference the indicator id from HTMX controls via `indicator='#…'`.

## Security

Escaping and `SafeUrl` / `TrustedHtml` are framework concerns; authorization and data
exposure remain application code. Redact secrets before rendering.

## Common mistakes

- Do not invent custom spinner CSS; use placement and the default theme.
- Do not copy docs-preview JavaScript into an application server.

## Testing

```python
from hedron import RenderMode, render

result = render(component, mode=RenderMode.FRAGMENT)
assert result.html
assert not result.diagnostics
```

[All component demos](index.md) · [Built-in API](../api/BUILT_INS.md) · [Testing](../guides/testing.md)

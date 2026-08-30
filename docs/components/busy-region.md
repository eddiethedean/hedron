---
title: BusyRegion
description: Generic HTMX busy host for region or document aria-busy and an optional indicator.
---

# `BusyRegion`

Generic HTMX busy host for region or document aria-busy and an optional indicator.

| | |
|---|---|
| Import | `from hedron_core.builtins import BusyRegion` |
| Distribution | `hedron-core` |
| Backend activity | No |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

<section class="hedron-component-demo" data-hedron-component-demo="BusyRegion"><div class="hdc-stage"><div class="hdc-result"><strong>BusyRegion</strong><span>Generic HTMX busy host for region or document aria-busy and an optional indicator.</span></div></div></section>

The preview is a local docs simulation (not a running Hedron server). Interactive demos show a “Simulated HTMX” trace when applicable.

## Basic use

```python
from hedron_core.builtins import BusyRegion, Text
component = BusyRegion(Text('Results'), scope='region', indicator='#busy')
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

BusyRegion and `Hx(busy=...)` mark opt-in HTMX busy hosts. Hedron UI sets aria-busy only on those hosts (document scope uses the document element), never on every request's body.

This component's core behavior is server-rendered HTML and does not require a browser runtime. The preview is ordinary semantic HTML, so keyboard, form, link, and disclosure behavior comes from the platform.

## Constructor and parameters

```text
BusyRegion(*nodes, children=None, scope='region', indicator=None)
```

| Parameter | Type | Meaning |
|---|---|---|
| `nodes` | `NodeLike` | Region content that becomes busy during HTMX requests. |
| `scope` | `'region' | 'document'` | Whether aria-busy applies to the region or document. |
| `indicator` | `str | None` | Optional #id selector for a busy indicator element. |

## Composition and backend behavior

Keep `BusyRegion` at the smallest semantic boundary. Fragment routes should return only
the replaced region and preserve stable target IDs across success, validation, empty,
loading, and error responses.

`BusyRegion` participates in interaction markup. Pair it with an explicit `@app.action` POST (and CSRF) when the control mutates state.

## Accessibility

Keep a visible or text status for busy; do not rely on color or motion alone.

## Security

Escaping and `SafeUrl` / `TrustedHtml` are framework concerns; authorization and data
exposure remain application code. Redact secrets before rendering.

## Common mistakes

- Indicator selectors must be simple #id tokens.
- Do not copy docs-preview JavaScript into an application server.

## Testing

```python
from hedron import RenderMode, render

result = render(component, mode=RenderMode.FRAGMENT)
assert result.html
assert not result.diagnostics
```

[All component demos](index.md) · [Built-in API](../api/BUILT_INS.md) · [Testing](../guides/testing.md)

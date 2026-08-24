---
title: AsyncRegion
description: Server-authored lifecycle boundary with ordinary fragment or page fallback.
---

# `AsyncRegion`

Server-authored lifecycle boundary with ordinary fragment or page fallback.
!!! note "Phase 0.61 published surface"

    This additive contract is implemented and verified for the published 0.61.x Supported surface. See [RELEASE_0_61](https://github.com/eddiethedean/hedron/blob/main/docs/acceptance/RELEASE_0_61.md).


| | |
|---|---|
| Import | `from hedron import AsyncRegion` |
| Distribution | `hedron` |
| Backend activity | No |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

<section class="hedron-component-demo" data-hedron-component-demo="AsyncRegion"><div class="hdc-stage"><div class="hdc-result"><strong>AsyncRegion</strong><span>Server-authored lifecycle boundary with ordinary fragment or page fallback.</span></div></div></section>

The preview is a local docs simulation (not a running Hedron server). Interactive demos show a “Simulated HTMX” trace when applicable.

## Basic use

```python
from hedron import AsyncRegion, Loading, Text

component = AsyncRegion(Text('Report ready'), state='success', pending=Text('Loading report…'), error=Text('Try again'))
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

AsyncRegion selects one state slot while rendering ordinary semantic HTML. It does not suspend Python, require hydration, or create a browser state store.

This component's core behavior is server-rendered HTML and does not require a browser runtime. The preview is ordinary semantic HTML, so keyboard, form, link, and disclosure behavior comes from the platform.

## Constructor and parameters

```python
AsyncRegion(*nodes, state='idle', initial=None, pending=None, empty=None, success=None, error=None, timeout=None, cancelled=None, stale=None, retry=None, conflict=None, fallback='fragment', label=None)
```

| Parameter | Type | Meaning |
|---|---|---|
| `state` | `idle | pending | empty | success | error | timeout | cancelled | stale | conflict` | Closed server-authored presentation state. |
| `state slots` | `NodeLike | None` | Optional initial, pending, empty, success, error, timeout, cancelled, stale, retry, and conflict content. |
| `fallback` | `fragment | page` | Ordinary enhancement-free response boundary. |
| `label` | `str | None` | Accessible label for the region and polite live status. |

## Composition and backend behavior

Keep `AsyncRegion` at the smallest semantic boundary. Fragment routes should return only
the replaced region and preserve stable target IDs across success, validation, empty,
loading, and error responses.

`AsyncRegion` participates in interaction markup. Pair it with an explicit `@action` / `@component` POST (and CSRF) when the control mutates state.

## Accessibility

Pending state exposes aria-busy; provide visible status text and keep recovery controls keyboard accessible.

## Security

Escaping and `SafeUrl` / `TrustedHtml` are framework concerns; authorization and data
exposure remain application code. Redact secrets before rendering.

## Common mistakes

- Do not use client state as authorization or omit an ordinary full-fragment/full-page fallback.
- Do not copy docs-preview JavaScript into an application server.

## Testing

```python
from hedron import RenderMode, render

result = render(component, mode=RenderMode.FRAGMENT)
assert result.html
assert not result.diagnostics
```

[All component demos](index.md) · [Built-in API](../api/BUILT_INS.md) · [Testing](../guides/testing.md)

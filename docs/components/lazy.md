---
title: Lazy
description: Load a component fragment when its placeholder enters the document.
---

# `Lazy`

Load a component fragment when its placeholder enters the document.

| | |
|---|---|
| Import | `from hedron import Lazy` |
| Distribution | `hedron` |
| Backend activity | Immediately after load |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

<section class="hedron-component-demo" data-hedron-component-demo="Lazy"><div class="hdc-stage"><div class="hdc-result" data-hdc-lazy aria-live="polite" aria-busy="true"><span class="hdc-skeleton"></span><span class="hdc-skeleton"></span><button class="hdc-button" type="button" data-hdc-action="lazy">Load activity</button></div></div><div class="hdc-request" data-hdc-request hidden><span>Simulated HTMX</span><code>GET /fragment → 200</code></div></section>

The preview is a local docs simulation (not a running Hedron server). Interactive demos show a “Simulated HTMX” trace when applicable.

## Basic use

```python
from hedron import Lazy, Skeleton

component = Lazy(ref=app.ref('activity-feed'), placeholder=Skeleton(lines=3), target_id='activity-feed')
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

Lazy emits a load-triggered HTMX request that targets its own collision-free container and swaps the response inside it. Repeated instances can share one ComponentRef safely. The initial node is busy and polite; the server fragment should clear busy state by replacing the placeholder.

This component can initiate or represent a backend interaction. The live documentation intercepts that interaction with JavaScript and shows the same pending, success, or replacement states without making a real request. In an application, keep the URL, authorization, validation, and returned fragment on the server; JavaScript is only progressive enhancement.

## Constructor and parameters

```python
Lazy(*, ref, placeholder=None, target_id=None)
```

| Parameter | Type | Meaning |
|---|---|---|
| `ref` | `ComponentRef` | Typed fragment endpoint. |
| `placeholder` | `NodeLike | None` | Initial content; defaults to Loading. |
| `target_id` | `str | None` | Explicit self-target ID; generated collision-free by default. |

## Composition and backend behavior

Keep `Lazy` at the smallest semantic boundary. Fragment routes should return only
the replaced region and preserve stable target IDs across success, validation, empty,
loading, and error responses.

Mutating flows must use POST, validate CSRF, authorize on the server, re-validate typed input, and return a bounded fragment. GET remains safe and repeatable; native submit should still work without HTMX.

## Accessibility

Choose a placeholder that reserves approximately the final space and provide meaningful loading text for material waits.

## Security

Escaping and `SafeUrl` / `TrustedHtml` are framework concerns; authorization and data
exposure remain application code. Redact secrets before rendering.

## Common mistakes

- Do not lazy-load content needed to understand or operate the initial page without a robust failure state.
- Do not copy docs-preview JavaScript into an application server.

## Testing

```python
from hedron import RenderMode, render

result = render(component, mode=RenderMode.FRAGMENT)
assert result.html
assert not result.diagnostics
```

[All component demos](index.md) · [Built-in API](../api/BUILT_INS.md) · [Testing](../guides/testing.md)

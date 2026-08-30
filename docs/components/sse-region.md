---
title: SseRegion
description: Typed SSE host that registers the sse extension and connects to a same-origin stream.
---

# `SseRegion`

Typed SSE host that registers the sse extension and connects to a same-origin stream.

| | |
|---|---|
| Import | `from hedron import SseRegion` |
| Distribution | `hedron` |
| Backend activity | No |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

<section class="hedron-component-demo" data-hedron-component-demo="SseRegion"><div class="hdc-stage"><div class="hdc-result"><strong>SseRegion</strong><span>Typed SSE host that registers the sse extension and connects to a same-origin stream.</span></div></div></section>

The preview is a local docs simulation (not a running Hedron server). Interactive demos show a “Simulated HTMX” trace when applicable.

## Basic use

```python
from hedron import SseRegion, Text

component = SseRegion(Text('Connecting…'), connect='/jobs/status', swap='message', close='done')
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

SseRegion wraps existing experimental SSE helpers with a demand-driven `sse` asset. Polling remains the Supported production fallback; do not treat this region as a correctness path.

This component's core behavior is server-rendered HTML and does not require a browser runtime. The preview is ordinary semantic HTML, so keyboard, form, link, and disclosure behavior comes from the platform.

## Constructor and parameters

```python
SseRegion(*children, *, connect, swap='message', close=None, id=None, class_=None)
```

| Parameter | Type | Meaning |
|---|---|---|
| `connect` | `SafeUrl | str` | Same-origin SSE endpoint (sse-connect). |
| `swap` | `str` | Closed sse-swap event token (default message). |
| `close` | `str | None` | Optional sse-close event that tears the stream down. |
| `id / class_` | `str | None` | Host element identity. |

## Composition and backend behavior

Keep `SseRegion` at the smallest semantic boundary. Fragment routes should return only
the replaced region and preserve stable target IDs across success, validation, empty,
loading, and error responses.

`SseRegion` participates in interaction markup. Pair it with an explicit `@app.action` POST (and CSRF) when the control mutates state.

## Accessibility

Keep a meaningful fallback child for no-JS and failed reconnect. Pair job streams with a Poll region on the same status.

## Security

Escaping and `SafeUrl` / `TrustedHtml` are framework concerns; authorization and data
exposure remain application code. Redact secrets before rendering.

## Common mistakes

- Do not point connect at user-derived or external URLs. Empty Page.htmx_extensions with SseRegion fails closed (HED-EXT-0004).
- Do not copy docs-preview JavaScript into an application server.

## Testing

```python
from hedron import RenderMode, render

result = render(component, mode=RenderMode.FRAGMENT)
assert result.html
assert not result.diagnostics
```

[All component demos](index.md) · [Built-in API](../api/BUILT_INS.md) · [Testing](../guides/testing.md)

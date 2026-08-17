---
title: SseTrigger
description: Listen for a named SSE event and optionally issue a cacheable GET swap.
---

# `SseTrigger`

Listen for a named SSE event and optionally issue a cacheable GET swap.

| | |
|---|---|
| Import | `from hedron import SseTrigger` |
| Distribution | `hedron` |
| Backend activity | No |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

<section class="hedron-component-demo" data-hedron-component-demo="SseTrigger"><div class="hdc-stage"><div class="hdc-result"><strong>SseTrigger</strong><span>Listen for a named SSE event and optionally issue a cacheable GET swap.</span></div></div></section>

The preview is a local docs simulation (not a running Hedron server). Interactive demos show a “Simulated HTMX” trace when applicable.

## Basic use

```python
from hedron import SseTrigger, Text

component = SseTrigger(Text('Waiting'), event='job-status', href='/jobs/panel', target='#job')
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

SseTrigger emits `hx-trigger="sse:<event>"` and registers the sse extension. It does not promote live transport to Supported.

This component's core behavior is server-rendered HTML and does not require a browser runtime. The preview is ordinary semantic HTML, so keyboard, form, link, and disclosure behavior comes from the platform.

## Constructor and parameters

```python
SseTrigger(*children, *, event, href=None, target=None, swap=None)
```

| Parameter | Type | Meaning |
|---|---|---|
| `event` | `str` | Closed sse-swap / sse: event token. |
| `href` | `SafeUrl | str | None` | Optional same-origin GET issued on the event. |
| `target / swap` | `str | None` | Optional hx-target and hx-swap for the GET. |

## Composition and backend behavior

Keep `SseTrigger` at the smallest semantic boundary. Fragment routes should return only
the replaced region and preserve stable target IDs across success, validation, empty,
loading, and error responses.

`SseTrigger` participates in interaction markup. Pair it with an explicit `@action` / `@component` POST (and CSRF) when the control mutates state.

## Accessibility

Announce resulting fragment swaps through existing live regions rather than inventing extra polite noise.

## Security

Escaping and `SafeUrl` / `TrustedHtml` are framework concerns; authorization and data
exposure remain application code. Redact secrets before rendering.

## Common mistakes

- Do not use SseTrigger for mutating methods. Prefer Poll when the stream is unavailable.
- Do not copy docs-preview JavaScript into an application server.

## Testing

```python
from hedron import RenderMode, render

result = render(component, mode=RenderMode.FRAGMENT)
assert result.html
assert not result.diagnostics
```

[All component demos](index.md) · [Built-in API](../api/BUILT_INS.md) · [Testing](../guides/testing.md)

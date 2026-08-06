---
title: MicrophoneCapture
description: Microphone capture file input (capture=user).
---

# `MicrophoneCapture`

Microphone capture file input (capture=user).

| | |
|---|---|
| Import | `from hedron import MicrophoneCapture` |
| Distribution | `hedron` |
| Backend activity | No |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

<section class="hedron-component-demo" data-hedron-component-demo="MicrophoneCapture"><div class="hdc-stage"><div class="hdc-result"><strong>MicrophoneCapture</strong><span>Microphone capture file input (capture=user).</span></div></div></section>

The preview is a local docs simulation (not a running Hedron server). Interactive demos show a “Simulated HTMX” trace when applicable.

## Basic use

```python
from hedron import MicrophoneCapture

component = MicrophoneCapture(name='clip')
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

Phase 0.15 surface. Prefer native HTML semantics and ordinary HTTP actions.

This component's core behavior is server-rendered HTML and does not require a browser runtime. The preview is ordinary semantic HTML, so keyboard, form, link, and disclosure behavior comes from the platform.

## Constructor and parameters

```python
MicrophoneCapture(name='audio')
```

| Parameter | Type | Meaning |
|---|---|---|
| `mark` | `str | None` | Optional stable test mark (`data-hedron-mark`). |

## Composition and backend behavior

Keep `MicrophoneCapture` at the smallest semantic boundary. Fragment routes should return only
the replaced region and preserve stable target IDs across success, validation, empty,
loading, and error responses.

This component is primarily presentational; keep any mutation on an explicit action or component route.

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

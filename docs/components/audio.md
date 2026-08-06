---
title: Audio
description: Accessible HTML audio player with SafeUrl source.
---

# `Audio`

Accessible HTML audio player with SafeUrl source.

| | |
|---|---|
| Import | `from hedron import Audio` |
| Distribution | `hedron` |
| Backend activity | No |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

<section class="hedron-component-demo" data-hedron-component-demo="Audio"><div class="hdc-stage"><div class="hdc-result"><strong>Audio</strong><span>Accessible HTML audio player with SafeUrl source.</span></div></div></section>

The preview is a local docs simulation (not a running Hedron server). Interactive demos show a “Simulated HTMX” trace when applicable.

## Basic use

```python
from hedron import Audio

component = Audio('/media/clip.mp3')
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

Phase 0.15 surface. Prefer native HTML semantics and ordinary HTTP actions.

This component's core behavior is server-rendered HTML and does not require a browser runtime. The preview is ordinary semantic HTML, so keyboard, form, link, and disclosure behavior comes from the platform.

## Constructor and parameters

```python
Audio(src, controls=True, autoplay=False)
```

| Parameter | Type | Meaning |
|---|---|---|
| `mark` | `str | None` | Optional stable test mark (`data-hedron-mark`). |

## Composition and backend behavior

Keep `Audio` at the smallest semantic boundary. Fragment routes should return only
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

---
title: Badge
description: Display compact categorical metadata with a named tone.
---

# `Badge`

Display compact categorical metadata with a named tone.

| | |
|---|---|
| Import | `from hedron import Badge` |
| Distribution | `hedron` |
| Backend activity | No |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

<section class="hedron-component-demo" data-hedron-component-demo="Badge"><div class="hdc-stage"><div class="hdc-inline"><span class="hdc-badge">Beta</span><span class="hdc-badge hdc-success">Healthy</span><span class="hdc-badge hdc-warning">Review</span></div></div></section>

The preview is a local docs simulation (not a running Hedron server). Interactive demos show a “Simulated HTMX” trace when applicable.

## Basic use

```python
from hedron import Badge, Inline

component = Inline(Badge('Beta', tone='info'), Badge('Healthy', tone='success'))
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

Badge emits visible text and a tone data attribute for theming. Tones are finite so products can keep color usage consistent.

This component's core behavior is server-rendered HTML and does not require a browser runtime. The preview is ordinary semantic HTML, so keyboard, form, link, and disclosure behavior comes from the platform.

## Constructor and parameters

```python
Badge(text, *, tone='neutral')
```

| Parameter | Type | Meaning |
|---|---|---|
| `text` | `str` | Short badge label. |
| `tone` | `neutral | info | success | warning | danger` | Semantic styling token. |

## Composition and backend behavior

Keep `Badge` at the smallest semantic boundary. Fragment routes should return only
the replaced region and preserve stable target IDs across success, validation, empty,
loading, and error responses.

`Badge` is primarily presentational; keep any mutation on an explicit action or component route.

## Accessibility

The text must carry the meaning; tone color is supplementary.

## Security

Escaping and `SafeUrl` / `TrustedHtml` are framework concerns; authorization and data
exposure remain application code. Redact secrets before rendering.

## Common mistakes

- Do not use a badge as a live announcement or interactive control.
- Do not copy docs-preview JavaScript into an application server.

## Testing

```python
from hedron import RenderMode, render

result = render(component, mode=RenderMode.FRAGMENT)
assert result.html
assert not result.diagnostics
```

[All component demos](index.md) · [Built-in API](../api/BUILT_INS.md) · [Testing](../guides/testing.md)

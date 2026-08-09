---
title: Metric
description: Display a labelled value and optional directional change.
---

# `Metric`

Display a labelled value and optional directional change.

| | |
|---|---|
| Import | `from hedron import Metric` |
| Distribution | `hedron` |
| Backend activity | No |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

<section class="hedron-component-demo" data-hedron-component-demo="Metric"><div class="hdc-stage"><dl class="hdc-metric"><dt>Monthly revenue</dt><dd>$84,200</dd><dd class="hdc-up" aria-label="change plus 8.4 percent">↗ +8.4%</dd></dl></div></section>

The preview is a local docs simulation (not a running Hedron server). Interactive demos show a “Simulated HTMX” trace when applicable.

## Basic use

```python
from hedron import Metric

component = Metric('Monthly revenue', '$84,200', delta='+8.4%', delta_tone='up')
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

Metric uses a description list so label, value, and delta remain related in non-visual reading. Tone is exposed as data for theming.

This component's core behavior is server-rendered HTML and does not require a browser runtime. The preview is ordinary semantic HTML, so keyboard, form, link, and disclosure behavior comes from the platform.

## Constructor and parameters

```python
Metric(label, value, *, delta=None, delta_tone='neutral')
```

| Parameter | Type | Meaning |
|---|---|---|
| `label` | `str` | Metric name. |
| `value` | `Any` | Current value converted to text. |
| `delta` | `Any | None` | Optional change. |
| `delta_tone` | `up | down | neutral` | Domain-aware direction token. |

## Composition and backend behavior

Keep `Metric` at the smallest semantic boundary. Fragment routes should return only
the replaced region and preserve stable target IDs across success, validation, empty,
loading, and error responses.

`Metric` is primarily presentational; keep any mutation on an explicit action or component route.

## Accessibility

Include a time window, unit, and whether up/down is good when context does not make that obvious.

## Security

Escaping and `SafeUrl` / `TrustedHtml` are framework concerns; authorization and data
exposure remain application code. Redact secrets before rendering.

## Common mistakes

- Never rely on green/red or arrows alone to explain the delta.
- Do not copy docs-preview JavaScript into an application server.

## Testing

```python
from hedron import RenderMode, render

result = render(component, mode=RenderMode.FRAGMENT)
assert result.html
assert not result.diagnostics
```

[All component demos](index.md) · [Built-in API](../api/BUILT_INS.md) · [Testing](../guides/testing.md)

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

The preview is intentionally small enough to inspect with a keyboard and screen reader. It demonstrates the component's semantic result, not a screenshot. If the example represents HTMX activity, the “Simulated HTMX” trace confirms that documentation JavaScript supplied the response locally.

## Basic use

```python
from hedron import Metric

component = Metric('Monthly revenue', '$84,200', delta='+8.4%', delta_tone='up')
```

In a route, return the component inside a `Page`, or return it directly as a fragment through the framework adapter. Components are immutable descriptions of output: construct the complete state on the server and let the renderer serialize it.

## How it works

Metric uses a description list so label, value, and delta remain related in non-visual reading. Tone is exposed as data for theming.

This component's core behavior is server-rendered HTML and does not require a browser runtime. The preview is ordinary semantic HTML, so keyboard, form, link, and disclosure behavior comes from the platform.

The component participates in Hedron's normal escaping, URL, and attribute validation. Values are data unless an API explicitly requires `SafeUrl` or reviewed `TrustedHtml`; do not pre-escape strings and do not concatenate HTML.

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

Keyword defaults are chosen for a safe, progressively enhanced baseline. Pass stable IDs when another component, a label, a URL fragment, a test, or an HTMX target must address the rendered node. Prefer typed component composition over hand-built HTML strings.

## Composition and backend behavior

Use `Metric` at the smallest level that owns its semantics. Page routes normally compose it under `Page`, `Main`, and an explicit heading structure. HTMX fragment routes should return only the region being replaced and keep stable target IDs across success, validation, empty, loading, and error responses.

This component is primarily presentational; keep any mutation on an explicit action or component route.

## Accessibility

Include a time window, unit, and whether up/down is good when context does not make that obvious.

Verify keyboard use, visible focus, zoom, and reduced motion for interactive states. Prefer native semantics and status/alert announcements over color-only cues.

## Security and validation

Escape and trust-boundary types (`SafeUrl`, `TrustedHtml`) remain framework concerns; authorization and data exposure remain yours. Redact secrets before rendering.

## Common mistakes

- Never rely on green/red or arrows alone to explain the delta.
- Do not copy docs-preview JavaScript into an application server; demos simulate HTMX locally.
- Choose components for semantics first, then theme them.

## Testing

```python
from hedron import RenderMode, render

result = render(component, mode=RenderMode.FRAGMENT)
assert result.html
assert not result.diagnostics
```

For interactive flows, assert method, URL, headers, fragment body, and status with a framework test client. Add a browser test when keyboard or HTMX swap behavior is material.

[All component demos](index.md) · [Built-in API baseline](../api/BUILT_INS.md) · [Testing UI](../guides/testing.md) · [Forms and actions](../guides/forms-and-actions.md)

---
title: MatplotlibChart
description: Render a Matplotlib figure as reviewed static SVG or image output.
---

# `MatplotlibChart`

Render a Matplotlib figure as reviewed static SVG or image output.

| | |
|---|---|
| Import | `from hedron import MatplotlibChart` |
| Distribution | `hedron-charts[matplotlib]` |
| Backend activity | No |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

<section class="hedron-component-demo" data-hedron-component-demo="MatplotlibChart"><div class="hdc-stage"><figure class="hdc-chart hdc-chart-bars"><figcaption><strong>MatplotlibChart output</strong><span>Accessible static preview with a text conclusion.</span></figcaption><div class="hdc-chart-art" role="img" aria-label="Sample chart showing a clear upward pattern"><i></i><i></i><i></i><i></i><i></i></div></figure></div></section>

The preview is intentionally small enough to inspect with a keyboard and screen reader. It demonstrates the component's semantic result, not a screenshot. If the example represents HTMX activity, the “Simulated HTMX” trace confirms that documentation JavaScript supplied the response locally.

Install the optional provider before importing this component:

```bash
pip install "hedron-charts[matplotlib]"
```

## Basic use

```python
from hedron import MatplotlibChart

component = MatplotlibChart(fig, title='Latency distribution', description='Most requests complete below 200 ms.')
```

In a route, return the component inside a `Page`, or return it directly as a fragment through the framework adapter. Components are immutable descriptions of output: construct the complete state on the server and let the renderer serialize it.

## How it works

The adapter compiles the figure server-side and renders inert output, avoiding a browser plotting runtime. SVG passes active-content rejection and output limits.

This component's core behavior is server-rendered HTML and does not require a browser runtime. The preview is ordinary semantic HTML, so keyboard, form, link, and disclosure behavior comes from the platform.

The component participates in Hedron's normal escaping, URL, and attribute validation. Values are data unless an API explicitly requires `SafeUrl` or reviewed `TrustedHtml`; do not pre-escape strings and do not concatenate HTML.

## Constructor and parameters

```python
MatplotlibChart(figure, *, title=None, description=None, alt=None, waiver=None, fmt='svg')
```

| Parameter | Type | Meaning |
|---|---|---|
| `figure` | `Matplotlib Figure` | Completed figure. |
| `title / description / alt` | `str | None` | Accessible metadata. |
| `waiver` | `str | None` | Reviewed exception. |
| `fmt` | `str` | Static output format. |

Keyword defaults are chosen for a safe, progressively enhanced baseline. Pass stable IDs when another component, a label, a URL fragment, a test, or an HTMX target must address the rendered node. Prefer typed component composition over hand-built HTML strings.

## Composition and backend behavior

Use `MatplotlibChart` at the smallest level that owns its semantics. Page routes normally compose it under `Page`, `Main`, and an explicit heading structure. HTMX fragment routes should return only the region being replaced and keep stable target IDs across success, validation, empty, loading, and error responses.

This component is primarily presentational; keep any mutation on an explicit action or component route.

## Accessibility

Do not rely only on labels embedded in a dense plot; provide a description and data summary.

Verify keyboard use, visible focus, zoom, and reduced motion for interactive states. Prefer native semantics and status/alert announcements over color-only cues.

## Security and validation

Escape and trust-boundary types (`SafeUrl`, `TrustedHtml`) remain framework concerns; authorization and data exposure remain yours. Redact secrets before rendering.

## Common mistakes

- Close figures after use in long-running processes and bound image dimensions and complexity.
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

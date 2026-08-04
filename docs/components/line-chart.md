---
title: LineChart
description: Plot one x/y series from row mappings with an accessible fallback.
---

# `LineChart`

Plot one x/y series from row mappings with an accessible fallback.

| | |
|---|---|
| Import | `from hedron import LineChart` |
| Distribution | `hedron[charts]` |
| Backend activity | No |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

<section class="hedron-component-demo" data-hedron-component-demo="LineChart"><div class="hdc-stage"><figure class="hdc-chart"><figcaption><strong>Monthly revenue</strong><span>Revenue rose from January through June.</span></figcaption><svg viewBox="0 0 360 150" role="img" aria-label="Revenue climbs from 18 to 42 thousand dollars"><path d="M20 125 L82 111 L144 91 L206 99 L268 55 L340 24" fill="none" stroke="currentColor" stroke-width="4"/><g fill="currentColor"><circle cx="20" cy="125" r="4"/><circle cx="82" cy="111" r="4"/><circle cx="144" cy="91" r="4"/><circle cx="206" cy="99" r="4"/><circle cx="268" cy="55" r="4"/><circle cx="340" cy="24" r="4"/></g></svg></figure></div></section>

The preview is intentionally small enough to inspect with a keyboard and screen reader. It demonstrates the component's semantic result, not a screenshot. If the example represents HTMX activity, the “Simulated HTMX” trace confirms that documentation JavaScript supplied the response locally.

Install the optional provider before importing this component:

```bash
pip install "hedron[charts]"
```

## Basic use

```python
from hedron import LineChart

component = LineChart(rows, x='month', y='revenue', title='Monthly revenue', description='Revenue rose from January through June.')
```

In a route, return the component inside a `Page`, or return it directly as a fragment through the framework adapter. Components are immutable descriptions of output: construct the complete state on the server and let the renderer serialize it.

## How it works

LineChart prefers the Matplotlib adapter when installed and otherwise produces a reviewed accessible SVG plus a redacted table fallback. Numeric and categorical x values are supported.

This component's core behavior is server-rendered HTML and does not require a browser runtime. The preview is ordinary semantic HTML, so keyboard, form, link, and disclosure behavior comes from the platform.

The component participates in Hedron's normal escaping, URL, and attribute validation. Values are data unless an API explicitly requires `SafeUrl` or reviewed `TrustedHtml`; do not pre-escape strings and do not concatenate HTML.

## Constructor and parameters

```python
LineChart(data, *, x, y, title, description=None, alt=None, waiver=None, limits=None)
```

| Parameter | Type | Meaning |
|---|---|---|
| `data` | `Sequence[Mapping]` | Bounded rows. |
| `x / y` | `str` | Source field names. |
| `title` | `str` | Required chart title. |
| `description / alt` | `str | None` | Text equivalents. |
| `waiver` | `str | None` | Reviewed accessibility exception. |
| `limits` | `VisualizationLimits | None` | Complexity bounds. |

Keyword defaults are chosen for a safe, progressively enhanced baseline. Pass stable IDs when another component, a label, a URL fragment, a test, or an HTMX target must address the rendered node. Prefer typed component composition over hand-built HTML strings.

## Composition and backend behavior

Use `LineChart` at the smallest level that owns its semantics. Page routes normally compose it under `Page`, `Main`, and an explicit heading structure. HTMX fragment routes should return only the region being replaced and keep stable target IDs across success, validation, empty, loading, and error responses.

This component is primarily presentational; keep any mutation on an explicit action or component route.

## Accessibility

Supply a conclusion-oriented description and keep the tabular fallback available to users who cannot perceive the plot.

Verify keyboard use, visible focus, zoom, and reduced motion for interactive states. Prefer native semantics and status/alert announcements over color-only cues.

## Security and validation

Escape and trust-boundary types (`SafeUrl`, `TrustedHtml`) remain framework concerns; authorization and data exposure remain yours. Redact secrets before rendering.

## Common mistakes

- Bound data and never insert raw labels into active SVG or bypass the accessibility contract.
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

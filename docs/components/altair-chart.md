---
title: AltairChart
description: Render an Altair chart through the declarative visualization adapter.
---

# `AltairChart`

Render an Altair chart through the declarative visualization adapter.

| | |
|---|---|
| Import | `from hedron_charts import AltairChart` |
| Distribution | `hedron-charts[altair]` |
| Backend activity | No |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

<section class="hedron-component-demo" data-hedron-component-demo="AltairChart"><div class="hdc-stage"><figure class="hdc-chart hdc-chart-scatter"><figcaption><strong>AltairChart output</strong><span>Accessible static preview with a text conclusion.</span></figcaption><div class="hdc-chart-art" role="img" aria-label="Sample chart showing a clear upward pattern"><i></i><i></i><i></i><i></i><i></i></div></figure></div></section>

The preview is a local docs simulation (not a running Hedron server). Interactive demos show a “Simulated HTMX” trace when applicable.

Install the optional provider before importing this component:

```bash
pip install "hedron-charts[altair]>=0.1.9,<0.2"
```

## Basic use

```python
from hedron_charts import AltairChart

component = AltairChart(chart, title='Deployments per week', description='Deployments peaked in week four.')
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

The server compiles the chart specification under output and accessibility limits. Hedron owns the embedding contract instead of accepting arbitrary active markup.

This component's core behavior is server-rendered HTML and does not require a browser runtime. The preview is ordinary semantic HTML, so keyboard, form, link, and disclosure behavior comes from the platform.

## Constructor and parameters

```python
AltairChart(chart, *, title=None, description=None, alt=None, waiver=None)
```

| Parameter | Type | Meaning |
|---|---|---|
| `chart` | `Altair Chart` | Declarative chart object. |
| `title / description / alt` | `str | None` | Accessible metadata. |
| `waiver` | `str | None` | Reviewed exception. |

## Composition and backend behavior

Keep `AltairChart` at the smallest semantic boundary. Fragment routes should return only
the replaced region and preserve stable target IDs across success, validation, empty,
loading, and error responses.

`AltairChart` renders data the server already prepared. Keep queries, authorization, and redaction on the route or data source — do not treat the component as a place for side effects.

## Accessibility

Use encodings that remain distinguishable without color and provide a narrative or table alternative.

## Security

Escaping and `SafeUrl` / `TrustedHtml` are framework concerns; authorization and data
exposure remain application code. Redact secrets before rendering.

## Common mistakes

- Validate data volume and avoid specifications that fetch remote resources in the browser.
- Do not copy docs-preview JavaScript into an application server.

## Testing

```python
from hedron import RenderMode, render

result = render(component, mode=RenderMode.FRAGMENT)
assert result.html
assert not result.diagnostics
```

[All component demos](index.md) · [Built-in API](../api/BUILT_INS.md) · [Testing](../guides/testing.md)

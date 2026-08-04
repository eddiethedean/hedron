---
title: DownloadButton
description: Download an authorized same-origin resource with a safe filename.
---

# `DownloadButton`

Download an authorized same-origin resource with a safe filename.

| | |
|---|---|
| Import | `from hedron import DownloadButton` |
| Distribution | `hedron` |
| Backend activity | On navigation |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

<section class="hedron-component-demo" data-hedron-component-demo="DownloadButton"><div class="hdc-stage"><div class="hdc-download"><span class="hdc-file-icon" aria-hidden="true">↓</span><span><strong>Service health export</strong><small>service-health.csv · 27 bytes</small></span><a class="hdc-button hdc-primary" href="data:text/csv;charset=utf-8,service%2Cstatus%0Aapi%2Chealthy" download="service-health.csv">Download CSV</a></div></div></section>

The preview is intentionally small enough to inspect with a keyboard and screen reader. It demonstrates the component's semantic result, not a screenshot. If the example represents HTMX activity, the “Simulated HTMX” trace confirms that documentation JavaScript supplied the response locally.

## Basic use

```python
from hedron import DownloadButton

component = DownloadButton(href='/exports/report.csv', filename='report.csv', label='Download CSV')
```

In a route, return the component inside a `Page`, or return it directly as a fragment through the framework adapter. Components are immutable descriptions of output: construct the complete state on the server and let the renderer serialize it.

## How it works

DownloadButton is a same-origin anchor with `download` and button styling. Pair it with `safe_download_response`, authorization, private no-store caching, and a validated basename on the server.

This component's core behavior is server-rendered HTML and does not require a browser runtime. The preview is ordinary semantic HTML, so keyboard, form, link, and disclosure behavior comes from the platform.

The component participates in Hedron's normal escaping, URL, and attribute validation. Values are data unless an API explicitly requires `SafeUrl` or reviewed `TrustedHtml`; do not pre-escape strings and do not concatenate HTML.

## Constructor and parameters

```python
DownloadButton(*, href=None, filename, label='Download', source=None)
```

| Parameter | Type | Meaning |
|---|---|---|
| `href / source` | `SafeUrl | str` | Required same-origin download endpoint. |
| `filename` | `str` | Validated suggested basename. |
| `label` | `str` | Visible action. |

Keyword defaults are chosen for a safe, progressively enhanced baseline. Pass stable IDs when another component, a label, a URL fragment, a test, or an HTMX target must address the rendered node. Prefer typed component composition over hand-built HTML strings.

## Composition and backend behavior

Use `DownloadButton` at the smallest level that owns its semantics. Page routes normally compose it under `Page`, `Main`, and an explicit heading structure. HTMX fragment routes should return only the region being replaced and keep stable target IDs across success, validation, empty, loading, and error responses.

Mutating flows must use POST, validate CSRF, authorize on the server, re-validate typed input, and return a bounded fragment. GET remains safe and repeatable; native submit should still work without HTMX.

## Accessibility

Include file type and, when known, size in nearby text so users understand the result.

Verify keyboard use, visible focus, zoom, and reduced motion for interactive states. Prefer native semantics and status/alert announcements over color-only cues.

## Security and validation

Escape and trust-boundary types (`SafeUrl`, `TrustedHtml`) remain framework concerns; authorization and data exposure remain yours. Redact secrets before rendering.

## Common mistakes

- A download attribute does not authorize access; the route must check permission on every request.
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

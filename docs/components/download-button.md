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

The preview is a local docs simulation (not a running Hedron server). Interactive demos show a “Simulated HTMX” trace when applicable.

## Basic use

```python
from hedron import DownloadButton
component = DownloadButton(href='/exports/report.csv', filename='report.csv', label='Download CSV')
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

DownloadButton is a same-origin anchor with `download` and button styling. Pair it with `safe_download_response`, authorization, private no-store caching, and a validated basename on the server.

This component's core behavior is server-rendered HTML and does not require a browser runtime. The preview is ordinary semantic HTML, so keyboard, form, link, and disclosure behavior comes from the platform.

## Constructor and parameters

```text
DownloadButton(*, href=None, filename, label='Download', source=None)
```

| Parameter | Type | Meaning |
|---|---|---|
| `href / source` | `SafeUrl | str` | Required same-origin download endpoint. |
| `filename` | `str` | Validated suggested basename. |
| `label` | `str` | Visible action. |

## Composition and backend behavior

Keep `DownloadButton` at the smallest semantic boundary. Fragment routes should return only
the replaced region and preserve stable target IDs across success, validation, empty,
loading, and error responses.

Mutating flows must use POST, validate CSRF, authorize on the server, re-validate typed input, and return a bounded fragment. GET remains safe and repeatable; native submit should still work without HTMX.

## Accessibility

Include file type and, when known, size in nearby text so users understand the result.

## Security

Escaping and `SafeUrl` / `TrustedHtml` are framework concerns; authorization and data
exposure remain application code. Redact secrets before rendering.

## Common mistakes

- A download attribute does not authorize access; the route must check permission on every request.
- Do not copy docs-preview JavaScript into an application server.

## Testing

```python
from hedron import RenderMode, render

result = render(component, mode=RenderMode.FRAGMENT)
assert result.html
assert not result.diagnostics
```

[All component demos](index.md) · [Built-in API](../api/BUILT_INS.md) · [Testing](../guides/testing.md)

---
title: OobHost
description: Stable out-of-band swap root with a reserved id.
---

# `OobHost`

Stable out-of-band swap root with a reserved id.

| | |
|---|---|
| Import | `from hedron import OobHost` |
| Distribution | `hedron` |
| Backend activity | No |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

<section class="hedron-component-demo" data-hedron-component-demo="OobHost"><div class="hdc-stage"><div class="hdc-fragment" id="demo-oob-host"><span class="hdc-badge">OOB host</span><span><strong>#status</strong><small>Stable swap root for out-of-band updates.</small></span></div></div></section>

The preview is a local docs simulation (not a running Hedron server). Interactive demos show a “Simulated HTMX” trace when applicable.

## Basic use

```python
from hedron import OobHost, Toast

component = OobHost(Toast('Saved'), id='toast-host')
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

OobHost reserves a predictable DOM root for `oob_swap` updates. Pair with authorize_oob_update and reserved-id rules so fragments cannot target arbitrary selectors.

This component's core behavior is server-rendered HTML and does not require a browser runtime. The preview is ordinary semantic HTML, so keyboard, form, link, and disclosure behavior comes from the platform.

## Constructor and parameters

```python
OobHost(*nodes, *, id, tag='div', class_=None)
```

| Parameter | Type | Meaning |
|---|---|---|
| `id` | `str` | Required stable element id for OOB targeting. |
| `tag` | `str` | Host element tag (default div). |
| `class_` | `str | None` | Optional CSS classes. |

## Composition and backend behavior

Keep `OobHost` at the smallest semantic boundary. Fragment routes should return only
the replaced region and preserve stable target IDs across success, validation, empty,
loading, and error responses.

This component is primarily presentational; keep any mutation on an explicit action or component route.

## Accessibility

Give each OOB host a unique page-local id and keep toast/status regions outside MainPanel when they must survive panel swaps.

## Security

Escaping and `SafeUrl` / `TrustedHtml` are framework concerns; authorization and data
exposure remain application code. Redact secrets before rendering.

## Common mistakes

- Do not reuse an OobHost id for ordinary fragment regions.
- Do not copy docs-preview JavaScript into an application server.

## Testing

```python
from hedron import RenderMode, render

result = render(component, mode=RenderMode.FRAGMENT)
assert result.html
assert not result.diagnostics
```

[All component demos](index.md) · [Built-in API](../api/BUILT_INS.md) · [Testing](../guides/testing.md)

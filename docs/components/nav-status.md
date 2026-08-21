---
title: NavStatus
description: Compact navigation status chip for shell sidebars.
---

# `NavStatus`

Compact navigation status chip for shell sidebars.

| | |
|---|---|
| Import | `from hedron import NavStatus` |
| Distribution | `hedron` |
| Backend activity | No |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

<section class="hedron-component-demo" data-hedron-component-demo="NavStatus"><div class="hdc-stage"><span class="hdc-chip">3 updates</span></div></section>

The preview is a local docs simulation (not a running Hedron server). Interactive demos show a “Simulated HTMX” trace when applicable.

## Basic use

```python
from hedron import NavStatus

component = NavStatus('3 updates', tone='info')
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

NavStatus is a chrome status marker for nav regions.

This component's core behavior is server-rendered HTML and does not require a browser runtime. The preview is ordinary semantic HTML, so keyboard, form, link, and disclosure behavior comes from the platform.

## Constructor and parameters

```python
NavStatus(label, *, tone='neutral', id=None, class_=None)
```

| Parameter | Type | Meaning |
|---|---|---|
| `label` | `str` | Status text. |
| `tone` | `neutral | info | success | warning | danger` | Semantic tone. |

## Composition and backend behavior

Keep `NavStatus` at the smallest semantic boundary. Fragment routes should return only
the replaced region and preserve stable target IDs across success, validation, empty,
loading, and error responses.

`NavStatus` is primarily presentational; keep any mutation on an explicit action or component route.

## Accessibility

Keep labels short so the chip remains scannable.

## Security

Escaping and `SafeUrl` / `TrustedHtml` are framework concerns; authorization and data
exposure remain application code. Redact secrets before rendering.

## Common mistakes

- Do not use NavStatus as a live region for assertive errors.
- Do not copy docs-preview JavaScript into an application server.

## Testing

```python
from hedron import RenderMode, render

result = render(component, mode=RenderMode.FRAGMENT)
assert result.html
assert not result.diagnostics
```

[All component demos](index.md) · [Built-in API](../api/BUILT_INS.md) · [Testing](../guides/testing.md)

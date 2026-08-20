---
title: FlowStep
description: One stage of a ProcessFlow with explicit status text.
---

# `FlowStep`

One stage of a ProcessFlow with explicit status text.

| | |
|---|---|
| Import | `from hedron import FlowStep` |
| Distribution | `hedron` |
| Backend activity | No |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

<section class="hedron-component-demo" data-hedron-component-demo="FlowStep"><div class="hdc-stage"><div class="hdc-stack"><span><b>Validate schemas</b><small>In progress · Checking required columns</small></span></div></div></section>

The preview is a local docs simulation (not a running Hedron server). Interactive demos show a “Simulated HTMX” trace when applicable.

## Basic use

```python
from hedron import FlowStep

component = FlowStep('Validate schemas', status='current', description='Checking required columns')
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

Each FlowStep renders a textual status so progress is understandable without color perception.

This component's core behavior is server-rendered HTML and does not require a browser runtime. The preview is ordinary semantic HTML, so keyboard, form, link, and disclosure behavior comes from the platform.

## Constructor and parameters

```python
FlowStep(label, *nodes, *, status='pending', description=None, status_text=None, id=None, class_=None)
```

| Parameter | Type | Meaning |
|---|---|---|
| `label` | `str` | Discernible step name. |
| `status` | `complete | current | pending | blocked | skipped` | Closed status vocabulary. |
| `description` | `str | None` | Optional supporting copy. |
| `status_text` | `str | None` | Optional override for the default status phrase. |

## Composition and backend behavior

Keep `FlowStep` at the smallest semantic boundary. Fragment routes should return only
the replaced region and preserve stable target IDs across success, validation, empty,
loading, and error responses.

`FlowStep` is primarily presentational; keep any mutation on an explicit action or component route.

## Accessibility

Mark exactly one step `current` unless the flow is idle or complete.

## Security

Escaping and `SafeUrl` / `TrustedHtml` are framework concerns; authorization and data
exposure remain application code. Redact secrets before rendering.

## Common mistakes

- Do not communicate status with icons alone; keep the status text.
- Do not copy docs-preview JavaScript into an application server.

## Testing

```python
from hedron import RenderMode, render

result = render(component, mode=RenderMode.FRAGMENT)
assert result.html
assert not result.diagnostics
```

[All component demos](index.md) · [Built-in API](../api/BUILT_INS.md) · [Testing](../guides/testing.md)

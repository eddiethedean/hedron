---
title: ProcessFlow
description: Accessible ordered workflow rendered as a process list.
---

# `ProcessFlow`

Accessible ordered workflow rendered as a process list.

| | |
|---|---|
| Import | `from hedron import ProcessFlow` |
| Distribution | `hedron` |
| Backend activity | No |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

<section class="hedron-component-demo" data-hedron-component-demo="ProcessFlow"><div class="hdc-stage"><ol class="hdc-list" aria-label="Release pipeline"><li><span>Ingest</span><small>Complete</small></li><li><span>Validate</span><small>In progress</small></li><li><span>Publish</span><small>Not started</small></li></ol></div></section>

The preview is a local docs simulation (not a running Hedron server). Interactive demos show a “Simulated HTMX” trace when applicable.

## Basic use

```python
from hedron import FlowStep, ProcessFlow

component = ProcessFlow(FlowStep('Ingest', status='complete'), FlowStep('Validate', status='current'), FlowStep('Publish'), label='Release pipeline')
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

ProcessFlow owns spacing and collapse through the default theme and requires FlowStep status text so state is never color-only.

This component's core behavior is server-rendered HTML and does not require a browser runtime. The preview is ordinary semantic HTML, so keyboard, form, link, and disclosure behavior comes from the platform.

## Constructor and parameters

```python
ProcessFlow(*steps, *, label, direction='horizontal', collapse='md', id=None, class_=None)
```

| Parameter | Type | Meaning |
|---|---|---|
| `steps` | `FlowStep` | Ordered FlowStep children. |
| `label` | `str` | Accessible name for the process list. |
| `direction` | `horizontal | vertical` | Closed layout direction. |
| `collapse` | `never | sm | md | lg` | Breakpoint where horizontal flows stack. |

## Composition and backend behavior

Keep `ProcessFlow` at the smallest semantic boundary. Fragment routes should return only
the replaced region and preserve stable target IDs across success, validation, empty,
loading, and error responses.

`ProcessFlow` is primarily presentational; keep any mutation on an explicit action or component route.

## Accessibility

Keep one ProcessFlow per operational workflow and update step status from the server.

## Security

Escaping and `SafeUrl` / `TrustedHtml` are framework concerns; authorization and data
exposure remain application code. Redact secrets before rendering.

## Common mistakes

- Do not use ProcessFlow for primary navigation—use Nav / NavLink.
- Do not copy docs-preview JavaScript into an application server.

## Testing

```python
from hedron import RenderMode, render

result = render(component, mode=RenderMode.FRAGMENT)
assert result.html
assert not result.diagnostics
```

[All component demos](index.md) · [Built-in API](../api/BUILT_INS.md) · [Testing](../guides/testing.md)

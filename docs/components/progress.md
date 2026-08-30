---
title: Progress
description: Show determinate completion with a native progress element.
---

# `Progress`

Show determinate completion with a native progress element.

| | |
|---|---|
| Import | `from hedron import Progress` |
| Distribution | `hedron` |
| Backend activity | No |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

<section class="hedron-component-demo" data-hedron-component-demo="Progress"><div class="hdc-stage"><div class="hdc-progress"><label for="demo-progress">Import progress</label><progress id="demo-progress" value="68" max="100">68%</progress><span>68%</span></div></div></section>

The preview is a local docs simulation (not a running Hedron server). Interactive demos show a “Simulated HTMX” trace when applicable.

## Basic use

```python
from hedron import Progress
component = Progress(68, maximum=100, label='Import progress')
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

The browser calculates completion from value and maximum and exposes native progress semantics. Render a separate numeric Text value when precise percentage matters visually.

This component's core behavior is server-rendered HTML and does not require a browser runtime. The preview is ordinary semantic HTML, so keyboard, form, link, and disclosure behavior comes from the platform.

## Constructor and parameters

```text
Progress(value, *, maximum=100, label=None)
```

| Parameter | Type | Meaning |
|---|---|---|
| `value` | `float` | Current progress. |
| `maximum` | `float` | Completion value. |
| `label` | `str | None` | Accessible name. |

## Composition and backend behavior

Keep `Progress` at the smallest semantic boundary. Fragment routes should return only
the replaced region and preserve stable target IDs across success, validation, empty,
loading, and error responses.

`Progress` is primarily presentational; keep any mutation on an explicit action or component route.

## Accessibility

Always provide a label unless nearby labelled context names the progress element.

## Security

Escaping and `SafeUrl` / `TrustedHtml` are framework concerns; authorization and data
exposure remain application code. Redact secrets before rendering.

## Common mistakes

- Use Loading or Status for indeterminate work; do not fake determinate values.
- Do not copy docs-preview JavaScript into an application server.

## Testing

```python
from hedron import RenderMode, render

result = render(component, mode=RenderMode.FRAGMENT)
assert result.html
assert not result.diagnostics
```

[All component demos](index.md) · [Built-in API](../api/BUILT_INS.md) · [Testing](../guides/testing.md)

---
title: Divider
description: Separate adjacent groups with a semantic horizontal or vertical rule.
---

# `Divider`

Separate adjacent groups with a semantic horizontal or vertical rule.

| | |
|---|---|
| Import | `from hedron import Divider` |
| Distribution | `hedron` |
| Backend activity | No |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

<section class="hedron-component-demo" data-hedron-component-demo="Divider"><div class="hdc-stage"><div class="hdc-divider-demo"><span>Overview</span><i role="separator" aria-orientation="vertical"></i><span>Activity</span></div></div></section>

The preview is a local docs simulation (not a running Hedron server). Interactive demos show a “Simulated HTMX” trace when applicable.

## Basic use

```python
from hedron import Divider, Inline, Text
component = Inline(Text('Overview'), Divider('vertical'), Text('Activity'))
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

A horizontal divider emits `<hr>`. A vertical divider emits an element with `role=separator` and `aria-orientation=vertical`, allowing the theme to size it for inline layouts.

This component's core behavior is server-rendered HTML and does not require a browser runtime. The preview is ordinary semantic HTML, so keyboard, form, link, and disclosure behavior comes from the platform.

## Constructor and parameters

```text
Divider(orientation='horizontal')
```

| Parameter | Type | Meaning |
|---|---|---|
| `orientation` | `'horizontal' | 'vertical'` | Separator direction. |

## Composition and backend behavior

Keep `Divider` at the smallest semantic boundary. Fragment routes should return only
the replaced region and preserve stable target IDs across success, validation, empty,
loading, and error responses.

`Divider` is primarily presentational; keep any mutation on an explicit action or component route.

## Accessibility

Use a divider only when the grouping is not already obvious from headings or whitespace.

## Security

Escaping and `SafeUrl` / `TrustedHtml` are framework concerns; authorization and data
exposure remain application code. Redact secrets before rendering.

## Common mistakes

- A vertical separator needs a layout that gives it visible height.
- Do not copy docs-preview JavaScript into an application server.

## Testing

```python
from hedron import RenderMode, render

result = render(component, mode=RenderMode.FRAGMENT)
assert result.html
assert not result.diagnostics
```

[All component demos](index.md) · [Built-in API](../api/BUILT_INS.md) · [Testing](../guides/testing.md)

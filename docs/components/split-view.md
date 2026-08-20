---
title: SplitView
description: Two-pane layout with closed ratio and responsive collapse.
---

# `SplitView`

Two-pane layout with closed ratio and responsive collapse.

| | |
|---|---|
| Import | `from hedron import SplitView` |
| Distribution | `hedron` |
| Backend activity | No |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

<section class="hedron-component-demo" data-hedron-component-demo="SplitView"><div class="hdc-stage"><div class="hdc-grid"><span><small>Source</small><strong>orders.csv</strong><em>Ready</em></span><span><small>Destination</small><strong>warehouse</strong><em>Connected</em></span></div></div></section>

The preview is a local docs simulation (not a running Hedron server). Interactive demos show a “Simulated HTMX” trace when applicable.

## Basic use

```python
from hedron import Card, SplitView, Text

component = SplitView(Card(Text('Source')), Card(Text('Destination')), ratio='2:1')
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

SplitView owns unequal column ratios through theme CSS so application authors never hand-write grid templates.

This component's core behavior is server-rendered HTML and does not require a browser runtime. The preview is ordinary semantic HTML, so keyboard, form, link, and disclosure behavior comes from the platform.

## Constructor and parameters

```python
SplitView(primary, secondary, *, ratio='1:1', collapse='md', gap='1rem', id=None, class_=None)
```

| Parameter | Type | Meaning |
|---|---|---|
| `primary / secondary` | `NodeLike` | Left and right panes. |
| `ratio` | `str` | Closed split ratio such as `1:1`, `2:1`, or `1:3`. |
| `collapse` | `str` | Breakpoint where panes stack (`never` / `sm` / `md` / `lg`). |

## Composition and backend behavior

Keep `SplitView` at the smallest semantic boundary. Fragment routes should return only
the replaced region and preserve stable target IDs across success, validation, empty,
loading, and error responses.

`SplitView` is primarily presentational; keep any mutation on an explicit action or component route.

## Accessibility

Prefer SplitView for source/destination or directory/detail workspaces.

## Security

Escaping and `SafeUrl` / `TrustedHtml` are framework concerns; authorization and data
exposure remain application code. Redact secrets before rendering.

## Common mistakes

- Do not pass arbitrary CSS grid templates; use the closed ratio set.
- Do not copy docs-preview JavaScript into an application server.

## Testing

```python
from hedron import RenderMode, render

result = render(component, mode=RenderMode.FRAGMENT)
assert result.html
assert not result.diagnostics
```

[All component demos](index.md) · [Built-in API](../api/BUILT_INS.md) · [Testing](../guides/testing.md)

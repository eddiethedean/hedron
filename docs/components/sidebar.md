---
title: Sidebar
description: Render complementary page content with an accessible label.
---

# `Sidebar`

Render complementary page content with an accessible label.

| | |
|---|---|
| Import | `from hedron import Sidebar` |
| Distribution | `hedron` |
| Backend activity | No |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

<section class="hedron-component-demo" data-hedron-component-demo="Sidebar"><div class="hdc-stage"><div class="hdc-shell"><aside aria-label="Workspace"><strong>Acme</strong><a href="#">Overview</a><a href="#">Settings</a></aside><main><h3>Overview</h3><p>Primary page content</p></main></div></div></section>

The preview is a local docs simulation (not a running Hedron server). Interactive demos show a “Simulated HTMX” trace when applicable.

## Basic use

```python
from hedron import Link, Nav, Sidebar
component = Sidebar(Nav(Link('Overview', '/'), Link('Settings', '/settings')), label='Workspace')
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

Sidebar emits an aside landmark with its label, while positioning and responsive behavior belong to the surrounding Grid and theme.

This component's core behavior is server-rendered HTML and does not require a browser runtime. The preview is ordinary semantic HTML, so keyboard, form, link, and disclosure behavior comes from the platform.

## Constructor and parameters

```text
Sidebar(*nodes, children=None, label='Sidebar', id=None, class_=None)
```

| Parameter | Type | Meaning |
|---|---|---|
| `nodes` | `NodeLike` | Positional complementary content. |
| `children` | `NodeLike | sequence | None` | Keyword content; combines with positional nodes. |
| `label` | `str` | Accessible region name. |
| `id` | `str | None` | Stable DOM target for the sidebar. |
| `class_` | `str | None` | Application class appended to `hedron-sidebar`. |

## Composition and backend behavior

Keep `Sidebar` at the smallest semantic boundary. Fragment routes should return only
the replaced region and preserve stable target IDs across success, validation, empty,
loading, and error responses.

`Sidebar` is primarily presentational; keep any mutation on an explicit action or component route.

## Accessibility

Use a distinct label when more than one aside exists and keep essential mobile actions available when the visual sidebar collapses.

## Security

Escaping and `SafeUrl` / `TrustedHtml` are framework concerns; authorization and data
exposure remain application code. Redact secrets before rendering.

## Common mistakes

- Sidebar does not create an application shell by itself; compose it explicitly with Main.
- Do not copy docs-preview JavaScript into an application server.

## Testing

```python
from hedron import RenderMode, render

result = render(component, mode=RenderMode.FRAGMENT)
assert result.html
assert not result.diagnostics
```

[All component demos](index.md) · [Built-in API](../api/BUILT_INS.md) · [Testing](../guides/testing.md)

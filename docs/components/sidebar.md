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

The preview is intentionally small enough to inspect with a keyboard and screen reader. It demonstrates the component's semantic result, not a screenshot. If the example represents HTMX activity, the “Simulated HTMX” trace confirms that documentation JavaScript supplied the response locally.

## Basic use

```python
from hedron import Link, Nav, Sidebar

component = Sidebar(Nav(Link('Overview', '/'), Link('Settings', '/settings')), label='Workspace')
```

In a route, return the component inside a `Page`, or return it directly as a fragment through the framework adapter. Components are immutable descriptions of output: construct the complete state on the server and let the renderer serialize it.

## How it works

Sidebar emits an aside landmark with its label, while positioning and responsive behavior belong to the surrounding Grid and theme.

This component's core behavior is server-rendered HTML and does not require a browser runtime. The preview is ordinary semantic HTML, so keyboard, form, link, and disclosure behavior comes from the platform.

The component participates in Hedron's normal escaping, URL, and attribute validation. Values are data unless an API explicitly requires `SafeUrl` or reviewed `TrustedHtml`; do not pre-escape strings and do not concatenate HTML.

## Constructor and parameters

```python
Sidebar(*nodes, children=None, label='Sidebar', id=None, class_=None)
```

| Parameter | Type | Meaning |
|---|---|---|
| `nodes` | `NodeLike` | Positional complementary content. |
| `children` | `NodeLike | sequence | None` | Keyword content; combines with positional nodes. |
| `label` | `str` | Accessible region name. |
| `id` | `str | None` | Stable DOM target for the sidebar. |
| `class_` | `str | None` | Application class appended to `hedron-sidebar`. |

Keyword defaults are chosen for a safe, progressively enhanced baseline. Pass stable IDs when another component, a label, a URL fragment, a test, or an HTMX target must address the rendered node. Prefer typed component composition over hand-built HTML strings.

## Composition and backend behavior

Use `Sidebar` at the smallest level that owns its semantics. Page routes normally compose it under `Page`, `Main`, and an explicit heading structure. HTMX fragment routes should return only the region being replaced and keep stable target IDs across success, validation, empty, loading, and error responses.

This component is primarily presentational; keep any mutation on an explicit action or component route.

## Accessibility

Use a distinct label when more than one aside exists and keep essential mobile actions available when the visual sidebar collapses.

Verify keyboard use, visible focus, zoom, and reduced motion for interactive states. Prefer native semantics and status/alert announcements over color-only cues.

## Security and validation

Escape and trust-boundary types (`SafeUrl`, `TrustedHtml`) remain framework concerns; authorization and data exposure remain yours. Redact secrets before rendering.

## Common mistakes

- Sidebar does not create an application shell by itself; compose it explicitly with Main.
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

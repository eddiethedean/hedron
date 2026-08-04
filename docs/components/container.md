---
title: Container
description: Constrain and center a readable block of page content.
---

# `Container`

Constrain and center a readable block of page content.

| | |
|---|---|
| Import | `from hedron import Container` |
| Distribution | `hedron` |
| Backend activity | No |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

<section class="hedron-component-demo" data-hedron-component-demo="Container"><div class="hdc-stage"><div class="hdc-container"><span class="hdc-eyebrow">Account settings</span><h3>Profile</h3><p>This readable block stays centered with a bounded width.</p><a href="#component-demo-result">Edit profile →</a></div></div></section>

The preview is intentionally small enough to inspect with a keyboard and screen reader. It demonstrates the component's semantic result, not a screenshot. If the example represents HTMX activity, the “Simulated HTMX” trace confirms that documentation JavaScript supplied the response locally.

## Basic use

```python
from hedron import Container, Heading, Text

component = Container(Heading('Profile', level=1), Text('Manage your public details.'), id='profile')
```

In a route, return the component inside a `Page`, or return it directly as a fragment through the framework adapter. Components are immutable descriptions of output: construct the complete state on the server and let the renderer serialize it.

## How it works

The component emits an addressable div and always retains the `hedron-container` theme hook. Positional nodes and `children=` use the same normalization rules, and an application class augments rather than disables the built-in layout. Width, gutters, and breakpoints remain theme CSS concerns.

This component's core behavior is server-rendered HTML and does not require a browser runtime. The preview is ordinary semantic HTML, so keyboard, form, link, and disclosure behavior comes from the platform.

The component participates in Hedron's normal escaping, URL, and attribute validation. Values are data unless an API explicitly requires `SafeUrl` or reviewed `TrustedHtml`; do not pre-escape strings and do not concatenate HTML.

## Constructor and parameters

```python
Container(*nodes, children=None, id=None, class_=None)
```

| Parameter | Type | Meaning |
|---|---|---|
| `nodes` | `NodeLike` | Positional content inside the width constraint. |
| `children` | `NodeLike | sequence | None` | Keyword alternative for generated or declarative child lists; combines with positional nodes. |
| `id` | `str | None` | Stable DOM target for links, tests, and HTMX swaps. |
| `class_` | `str | None` | Application class appended after `hedron-container`; the built-in theme hook is retained. |

Keyword defaults are chosen for a safe, progressively enhanced baseline. Pass stable IDs when another component, a label, a URL fragment, a test, or an HTMX target must address the rendered node. Prefer typed component composition over hand-built HTML strings.

## Composition and backend behavior

Use `Container` at the smallest level that owns its semantics. Page routes normally compose it under `Page`, `Main`, and an explicit heading structure. HTMX fragment routes should return only the region being replaced and keep stable target IDs across success, validation, empty, loading, and error responses.

This component is primarily presentational; keep any mutation on an explicit action or component route.

## Accessibility

A container has no semantics of its own, so keep headings and landmarks inside it.

Verify keyboard use, visible focus, zoom, and reduced motion for interactive states. Prefer native semantics and status/alert announcements over color-only cues.

## Security and validation

Escape and trust-boundary types (`SafeUrl`, `TrustedHtml`) remain framework concerns; authorization and data exposure remain yours. Redact secrets before rendering.

## Common mistakes

- Do not use Container as a substitute for Main or Section.
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

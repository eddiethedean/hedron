---
title: Expander
description: Reveal optional content with native details/summary behavior.
---

# `Expander`

Reveal optional content with native details/summary behavior.

| | |
|---|---|
| Import | `from hedron import Expander` |
| Distribution | `hedron` |
| Backend activity | No |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

<section class="hedron-component-demo" data-hedron-component-demo="Expander"><div class="hdc-stage"><details class="hdc-expander"><summary>Advanced settings</summary><p>Configure retry and timeout behavior.</p></details></div></section>

The preview is intentionally small enough to inspect with a keyboard and screen reader. It demonstrates the component's semantic result, not a screenshot. If the example represents HTMX activity, the “Simulated HTMX” trace confirms that documentation JavaScript supplied the response locally.

## Basic use

```python
from hedron import Expander, Text

component = Expander('Advanced settings', Text('Configure retry and timeout behavior.'))
```

In a route, return the component inside a `Page`, or return it directly as a fragment through the framework adapter. Components are immutable descriptions of output: construct the complete state on the server and let the renderer serialize it.

## How it works

The native details element supplies keyboard and disclosure state without custom JavaScript. Content remains in the document and participates in search.

This component's core behavior is server-rendered HTML and does not require a browser runtime. The preview is ordinary semantic HTML, so keyboard, form, link, and disclosure behavior comes from the platform.

The component participates in Hedron's normal escaping, URL, and attribute validation. Values are data unless an API explicitly requires `SafeUrl` or reviewed `TrustedHtml`; do not pre-escape strings and do not concatenate HTML.

## Constructor and parameters

```python
Expander(title, *nodes, children=None, open=False, id=None, class_=None)
```

| Parameter | Type | Meaning |
|---|---|---|
| `title` | `str` | Visible summary label. |
| `nodes` | `NodeLike` | Positional disclosure content. |
| `children` | `NodeLike | sequence | None` | Keyword disclosure content; combines with positional nodes. |
| `open` | `bool` | Initial expanded state. |
| `id` | `str | None` | Stable ID for links, tests, or replacement. |
| `class_` | `str | None` | Application class appended to `hedron-expander`. |

Keyword defaults are chosen for a safe, progressively enhanced baseline. Pass stable IDs when another component, a label, a URL fragment, a test, or an HTMX target must address the rendered node. Prefer typed component composition over hand-built HTML strings.

## Composition and backend behavior

Use `Expander` at the smallest level that owns its semantics. Page routes normally compose it under `Page`, `Main`, and an explicit heading structure. HTMX fragment routes should return only the region being replaced and keep stable target IDs across success, validation, empty, loading, and error responses.

This component is primarily presentational; keep any mutation on an explicit action or component route.

## Accessibility

Use a summary that describes the hidden content, not a generic “More”.

Verify keyboard use, visible focus, zoom, and reduced motion for interactive states. Prefer native semantics and status/alert announcements over color-only cues.

## Security and validation

Escape and trust-boundary types (`SafeUrl`, `TrustedHtml`) remain framework concerns; authorization and data exposure remain yours. Redact secrets before rendering.

## Common mistakes

- Do not hide required fields or primary instructions in a collapsed expander.
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

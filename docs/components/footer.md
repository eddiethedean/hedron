---
title: Footer
description: Render the semantic `footer` landmark for closing information for a page or section.
---

# `Footer`

Render the semantic `footer` landmark for closing information for a page or section.

| | |
|---|---|
| Import | `from hedron import Footer` |
| Distribution | `hedron` |
| Backend activity | No |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

<section class="hedron-component-demo" data-hedron-component-demo="Footer"><div class="hdc-stage"><footer class="hdc-landmark"><span>&lt;footer&gt;</span><strong>Footer content</strong><p>Render the semantic `footer` landmark for closing information for a page or section.</p></footer></div></section>

The preview is intentionally small enough to inspect with a keyboard and screen reader. It demonstrates the component's semantic result, not a screenshot. If the example represents HTMX activity, the “Simulated HTMX” trace confirms that documentation JavaScript supplied the response locally.

## Basic use

```python
from hedron import Footer, Heading, Text

component = Footer(Heading('Support', level=2), Text('Contact the platform team'))
```

In a route, return the component inside a `Page`, or return it directly as a fragment through the framework adapter. Components are immutable descriptions of output: construct the complete state on the server and let the renderer serialize it.

## How it works

`Footer` emits a native `<footer>`, preserving semantic navigation instead of using a generic div. Children may be passed individually or as one non-string sequence.

This component's core behavior is server-rendered HTML and does not require a browser runtime. The preview is ordinary semantic HTML, so keyboard, form, link, and disclosure behavior comes from the platform.

The component participates in Hedron's normal escaping, URL, and attribute validation. Values are data unless an API explicitly requires `SafeUrl` or reviewed `TrustedHtml`; do not pre-escape strings and do not concatenate HTML.

## Constructor and parameters

```python
Footer(*nodes, children=None, class_=None, id=None)
```

| Parameter | Type | Meaning |
|---|---|---|
| `nodes` | `NodeLike` | Positional content belonging to this semantic region. |
| `children` | `NodeLike | sequence | None` | Keyword alternative; combines with positional nodes. |
| `class_` | `str | None` | Optional authored class name. |
| `id` | `str | None` | Stable fragment or target identifier. |

Keyword defaults are chosen for a safe, progressively enhanced baseline. Pass stable IDs when another component, a label, a URL fragment, a test, or an HTMX target must address the rendered node. Prefer typed component composition over hand-built HTML strings.

## Composition and backend behavior

Use `Footer` at the smallest level that owns its semantics. Page routes normally compose it under `Page`, `Main`, and an explicit heading structure. HTMX fragment routes should return only the region being replaced and keep stable target IDs across success, validation, empty, loading, and error responses.

This component is primarily presentational; keep any mutation on an explicit action or component route.

## Accessibility

Use explicit link text and keep legal or support navigation grouped meaningfully.

Verify keyboard use, visible focus, zoom, and reduced motion for interactive states. Prefer native semantics and status/alert announcements over color-only cues.

## Security and validation

Escape and trust-boundary types (`SafeUrl`, `TrustedHtml`) remain framework concerns; authorization and data exposure remain yours. Redact secrets before rendering.

## Common mistakes

- A nested section footer is not the page-wide contentinfo landmark.
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

---
title: Markdown
description: Render Markdown through the optional, escaped content pipeline.
---

# `Markdown`

Render Markdown through the optional, escaped content pipeline.

| | |
|---|---|
| Import | `from hedron import Markdown` |
| Distribution | `hedron[markdown]` |
| Backend activity | No |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

<section class="hedron-component-demo" data-hedron-component-demo="Markdown"><div class="hdc-stage"><article class="hdc-markdown"><h2>Release notes</h2><ul><li>Safer URLs</li><li>Faster rendering</li></ul><blockquote>Generated from Markdown source.</blockquote></article></div></section>

The preview is intentionally small enough to inspect with a keyboard and screen reader. It demonstrates the component's semantic result, not a screenshot. If the example represents HTMX activity, the “Simulated HTMX” trace confirms that documentation JavaScript supplied the response locally.

Install the optional provider before importing this component:

```bash
pip install "hedron[markdown]"
```

## Basic use

```python
from hedron import Markdown

component = Markdown("## Release notes\n\n- Safer URLs\n- Faster rendering")
```

In a route, return the component inside a `Page`, or return it directly as a fragment through the framework adapter. Components are immutable descriptions of output: construct the complete state on the server and let the renderer serialize it.

## How it works

Markdown uses the optional markdown dependency and returns reviewed rendered output. Raw HTML handling and sanitization are governed by the content pipeline; it is not a shortcut around TrustedHtml.

This component's core behavior is server-rendered HTML and does not require a browser runtime. The preview is ordinary semantic HTML, so keyboard, form, link, and disclosure behavior comes from the platform.

The component participates in Hedron's normal escaping, URL, and attribute validation. Values are data unless an API explicitly requires `SafeUrl` or reviewed `TrustedHtml`; do not pre-escape strings and do not concatenate HTML.

## Constructor and parameters

```python
Markdown(source)
```

| Parameter | Type | Meaning |
|---|---|---|
| `source` | `str` | Markdown source text. |

Keyword defaults are chosen for a safe, progressively enhanced baseline. Pass stable IDs when another component, a label, a URL fragment, a test, or an HTMX target must address the rendered node. Prefer typed component composition over hand-built HTML strings.

## Composition and backend behavior

Use `Markdown` at the smallest level that owns its semantics. Page routes normally compose it under `Page`, `Main`, and an explicit heading structure. HTMX fragment routes should return only the region being replaced and keep stable target IDs across success, validation, empty, loading, and error responses.

This component is primarily presentational; keep any mutation on an explicit action or component route.

## Accessibility

Authors still own heading hierarchy, meaningful link text, table captions, and image alternatives in the source.

Verify keyboard use, visible focus, zoom, and reduced motion for interactive states. Prefer native semantics and status/alert announcements over color-only cues.

## Security and validation

Escape and trust-boundary types (`SafeUrl`, `TrustedHtml`) remain framework concerns; authorization and data exposure remain yours. Redact secrets before rendering.

## Common mistakes

- Install `hedron[markdown]` and never assume arbitrary embedded HTML is trusted.
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

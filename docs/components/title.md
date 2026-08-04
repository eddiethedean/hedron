---
title: Title
description: Set the browser-tab and history-entry title.
---

# `Title`

Set the browser-tab and history-entry title.

| | |
|---|---|
| Import | `from hedron import Title` |
| Distribution | `hedron` |
| Backend activity | No |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

<section class="hedron-component-demo" data-hedron-component-demo="Title"><div class="hdc-stage"><div class="hdc-browser"><div><i></i><i></i><i></i><span>Billing · Acme</span></div><main><dl class="hdc-description"><dt>title</dt><dd>Billing · Acme</dd><dt>description</dt><dd>Manage billing</dd></dl></main></div></div></section>

The preview is intentionally small enough to inspect with a keyboard and screen reader. It demonstrates the component's semantic result, not a screenshot. If the example represents HTMX activity, the “Simulated HTMX” trace confirms that documentation JavaScript supplied the response locally.

## Basic use

```python
from hedron import Title

component = Title('Billing · Acme')
```

In a route, return the component inside a `Page`, or return it directly as a fragment through the framework adapter. Components are immutable descriptions of output: construct the complete state on the server and let the renderer serialize it.

## How it works

`Title` emits exactly one `<title>` element. Put it in a `Head`, or use the simpler `title=` argument on `Page`.

This component's core behavior is server-rendered HTML and does not require a browser runtime. The preview is ordinary semantic HTML, so keyboard, form, link, and disclosure behavior comes from the platform.

The component participates in Hedron's normal escaping, URL, and attribute validation. Values are data unless an API explicitly requires `SafeUrl` or reviewed `TrustedHtml`; do not pre-escape strings and do not concatenate HTML.

## Constructor and parameters

```python
Title(text=None, *, children=None)
```

| Parameter | Type | Meaning |
|---|---|---|
| `text` | `str | None` | Preferred title text. |
| `children` | `str | None` | Alternative authoring form when `text` is omitted. |

Keyword defaults are chosen for a safe, progressively enhanced baseline. Pass stable IDs when another component, a label, a URL fragment, a test, or an HTMX target must address the rendered node. Prefer typed component composition over hand-built HTML strings.

## Composition and backend behavior

Use `Title` at the smallest level that owns its semantics. Page routes normally compose it under `Page`, `Main`, and an explicit heading structure. HTMX fragment routes should return only the region being replaced and keep stable target IDs across success, validation, empty, loading, and error responses.

This component is primarily presentational; keep any mutation on an explicit action or component route.

## Accessibility

Use a concise, unique title whose most specific information comes first.

Verify keyboard use, visible focus, zoom, and reduced motion for interactive states. Prefer native semantics and status/alert announcements over color-only cues.

## Security and validation

Escape and trust-boundary types (`SafeUrl`, `TrustedHtml`) remain framework concerns; authorization and data exposure remain yours. Redact secrets before rendering.

## Common mistakes

- This is document metadata, not a visible heading. Pair it with a page `Heading(level=1)`.
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

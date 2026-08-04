---
title: Page
description: Render a complete HTML document with safe head defaults and a body.
---

# `Page`

Render a complete HTML document with safe head defaults and a body.

| | |
|---|---|
| Import | `from hedron import Page` |
| Distribution | `hedron` |
| Backend activity | Page response |
| Normal render mode | `RenderMode.PAGE` |

## Live demo

<section class="hedron-component-demo" data-hedron-component-demo="Page"><div class="hdc-stage"><div class="hdc-browser"><div><i></i><i></i><i></i><span data-hdc-title>Account · Acme</span></div><main><h3>Account</h3><p>Signed in as ada@example.com</p></main></div></div></section>

The preview is intentionally small enough to inspect with a keyboard and screen reader. It demonstrates the component's semantic result, not a screenshot. If the example represents HTMX activity, the “Simulated HTMX” trace confirms that documentation JavaScript supplied the response locally.

## Basic use

```python
from hedron import Header, Heading, Main, Page, Text

component = Page(Header(Heading('Account', level=1)), Main(Text('Signed in')), title='Account')
```

In a route, return the component inside a `Page`, or return it directly as a fragment through the framework adapter. Components are immutable descriptions of output: construct the complete state on the server and let the renderer serialize it.

## How it works

`Page` owns the outer `html`, `head`, and `body` elements. It always emits UTF-8 and responsive viewport metadata, then adds the title and optional head slot before rendering body children.

This component's core behavior is server-rendered HTML and does not require a browser runtime. The preview is ordinary semantic HTML, so keyboard, form, link, and disclosure behavior comes from the platform.

The component participates in Hedron's normal escaping, URL, and attribute validation. Values are data unless an API explicitly requires `SafeUrl` or reviewed `TrustedHtml`; do not pre-escape strings and do not concatenate HTML.

## Constructor and parameters

```python
Page(*body, lang='en', title=None, head=None, children=None, data_theme=None)
```

| Parameter | Type | Meaning |
|---|---|---|
| `body / children` | `NodeLike` | Body nodes; use either positional children or `children=`. |
| `lang` | `str` | The document language written to `<html lang>`. |
| `title` | `str | None` | Convenience document title. |
| `head` | `NodeLike | None` | Additional trusted head nodes. |
| `data_theme` | `str | None` | Initial `data-theme` value. |

Keyword defaults are chosen for a safe, progressively enhanced baseline. Pass stable IDs when another component, a label, a URL fragment, a test, or an HTMX target must address the rendered node. Prefer typed component composition over hand-built HTML strings.

## Composition and backend behavior

Use `Page` at the smallest level that owns its semantics. Page routes normally compose it under `Page`, `Main`, and an explicit heading structure. HTMX fragment routes should return only the region being replaced and keep stable target IDs across success, validation, empty, loading, and error responses.

This component is primarily presentational; keep any mutation on an explicit action or component route.

## Accessibility

Set `lang` to the language of the page and keep exactly one main landmark in the body.

Verify keyboard use, visible focus, zoom, and reduced motion for interactive states. Prefer native semantics and status/alert announcements over color-only cues.

## Security and validation

Escape and trust-boundary types (`SafeUrl`, `TrustedHtml`) remain framework concerns; authorization and data exposure remain yours. Redact secrets before rendering.

## Common mistakes

- Do not return `Page` for an HTMX fragment request; use `Fragment` and fragment render mode instead.
- Do not copy docs-preview JavaScript into an application server; demos simulate HTMX locally.
- Choose components for semantics first, then theme them.

## Testing

```python
from hedron import RenderMode, render

result = render(component, mode=RenderMode.PAGE)
assert result.html
assert not result.diagnostics
```

For interactive flows, assert method, URL, headers, fragment body, and status with a framework test client. Add a browser test when keyboard or HTMX swap behavior is material.

[All component demos](index.md) · [Built-in API baseline](../api/BUILT_INS.md) · [Testing UI](../guides/testing.md) · [Forms and actions](../guides/forms-and-actions.md)

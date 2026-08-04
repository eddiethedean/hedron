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

Use `Page` at the smallest level that owns its semantics. Page routes normally compose it under `Page`, `Main`, and an explicit heading structure. HTMX routes should return only the component region being replaced and should preserve stable target IDs across success, validation, empty, loading, and error responses.

When a request can mutate data, use POST, validate CSRF, authenticate and authorize on the server, validate typed input again, and return a bounded fragment. GET interactions must remain safe and repeatable. Native links and forms should still reach a useful server response when HTMX is unavailable.

## Accessibility

Set `lang` to the language of the page and keep exactly one main landmark in the body.

Test the demo and your application with keyboard-only input, visible focus, zoom, reduced motion, and at least one screen reader. Never make color, position, animation, or an icon the only carrier of state. Dynamic results need an appropriate status or alert and a deliberate focus strategy.

## Security and validation

Treat all request data, database content, filenames, URLs, labels, chart data, and Markdown as untrusted until the owning boundary validates it. Hedron escapes text and constrains dangerous surfaces, but it cannot decide application authorization or data exposure. Keep responses bounded, redact secrets before rendering, and use the narrowest URL and trust types available.

## Common mistakes

- Do not return `Page` for an HTMX fragment request; use `Fragment` and fragment render mode instead.
- Do not copy the demo's JavaScript into a server application as a substitute for an HTMX endpoint. The simulation exists only because the hosted docs have no application backend.
- Do not select components by visual appearance alone; choose the native semantics first, then theme them.

## Testing

Render the component at the boundary you intend to ship and assert behavior rather than a large, brittle snapshot:

```python
from hedron import RenderMode, render

result = render(component, mode=RenderMode.PAGE)
assert result.html
assert not result.diagnostics
```

For interactive use, add a framework test that sends the same method, URL, headers, and typed payload as the browser, then assert the returned fragment, status code, cache policy, and security headers. Add a browser test for keyboard behavior, focus, live announcements, and the HTMX swap lifecycle when those behaviors are material.

[All component demos](index.md) · [Built-in API baseline](../api/BUILT_INS.md) · [Testing UI](../guides/testing.md)

---
title: Stack
description: Arrange children vertically with a validated, consistent gap.
---

# `Stack`

Arrange children vertically with a validated, consistent gap.

| | |
|---|---|
| Import | `from hedron import Stack` |
| Distribution | `hedron` |
| Backend activity | No |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

<section class="hedron-component-demo" data-hedron-component-demo="Stack"><div class="hdc-stage"><div class="hdc-stack"><span><b>Build completed</b><small>42 seconds ago</small></span><span><b>Preview deployed</b><small>Environment ready</small></span><span><b>Review requested</b><small>2 teammates notified</small></span></div></div></section>

The preview is intentionally small enough to inspect with a keyboard and screen reader. It demonstrates the component's semantic result, not a screenshot. If the example represents HTMX activity, the “Simulated HTMX” trace confirms that documentation JavaScript supplied the response locally.

## Basic use

```python
from hedron import Button, Heading, Stack, Text

component = Stack(Heading('Settings', level=2), Text('Profile'), Button('Save'), gap='1.25rem')
```

In a route, return the component inside a `Page`, or return it directly as a fragment through the framework adapter. Components are immutable descriptions of output: construct the complete state on the server and let the renderer serialize it.

## How it works

`Stack` writes layout intent and the validated gap to data attributes consumed by the theme; the shipped theme applies that exact gap without requiring an unsafe inline style. Its built-in class is retained when you add an application class. DOM order is unchanged, so the visual sequence matches reading and keyboard order.

This component's core behavior is server-rendered HTML and does not require a browser runtime. The preview is ordinary semantic HTML, so keyboard, form, link, and disclosure behavior comes from the platform.

The component participates in Hedron's normal escaping, URL, and attribute validation. Values are data unless an API explicitly requires `SafeUrl` or reviewed `TrustedHtml`; do not pre-escape strings and do not concatenate HTML.

## Constructor and parameters

```python
Stack(*nodes, children=None, gap='1rem', id=None, class_=None)
```

| Parameter | Type | Meaning |
|---|---|---|
| `nodes` | `NodeLike` | Positional items in visual and DOM order. |
| `children` | `NodeLike | sequence | None` | Keyword child list; combines with positional nodes. |
| `gap` | `CSS length` | Validated `rem`, `em`, `px`, or `%` spacing. |
| `id` | `str | None` | Stable DOM target for the stack region. |
| `class_` | `str | None` | Optional class appended to `hedron-stack`. |

Keyword defaults are chosen for a safe, progressively enhanced baseline. Pass stable IDs when another component, a label, a URL fragment, a test, or an HTMX target must address the rendered node. Prefer typed component composition over hand-built HTML strings.

## Composition and backend behavior

Use `Stack` at the smallest level that owns its semantics. Page routes normally compose it under `Page`, `Main`, and an explicit heading structure. HTMX routes should return only the component region being replaced and should preserve stable target IDs across success, validation, empty, loading, and error responses.

When a request can mutate data, use POST, validate CSRF, authenticate and authorize on the server, validate typed input again, and return a bounded fragment. GET interactions must remain safe and repeatable. Native links and forms should still reach a useful server response when HTMX is unavailable.

## Accessibility

Keep DOM order meaningful and never use CSS reordering to change the task sequence.

Test the demo and your application with keyboard-only input, visible focus, zoom, reduced motion, and at least one screen reader. Never make color, position, animation, or an icon the only carrier of state. Dynamic results need an appropriate status or alert and a deliberate focus strategy.

## Security and validation

Treat all request data, database content, filenames, URLs, labels, chart data, and Markdown as untrusted until the owning boundary validates it. Hedron escapes text and constrains dangerous surfaces, but it cannot decide application authorization or data exposure. Keep responses bounded, redact secrets before rendering, and use the narrowest URL and trust types available.

## Common mistakes

- Values such as `calc(...)`, viewport units, and arbitrary CSS are rejected; use a supported length token.
- Do not copy the demo's JavaScript into a server application as a substitute for an HTMX endpoint. The simulation exists only because the hosted docs have no application backend.
- Do not select components by visual appearance alone; choose the native semantics first, then theme them.

## Testing

Render the component at the boundary you intend to ship and assert behavior rather than a large, brittle snapshot:

```python
from hedron import RenderMode, render

result = render(component, mode=RenderMode.FRAGMENT)
assert result.html
assert not result.diagnostics
```

For interactive use, add a framework test that sends the same method, URL, headers, and typed payload as the browser, then assert the returned fragment, status code, cache policy, and security headers. Add a browser test for keyboard behavior, focus, live announcements, and the HTMX swap lifecycle when those behaviors are material.

[All component demos](index.md) · [Built-in API baseline](../api/BUILT_INS.md) · [Testing UI](../guides/testing.md)

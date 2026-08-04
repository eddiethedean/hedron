---
title: FormField
description: Bind a label, help text, required state, and field error to one control.
---

# `FormField`

Bind a label, help text, required state, and field error to one control.

| | |
|---|---|
| Import | `from hedron import FormField` |
| Distribution | `hedron` |
| Backend activity | No |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

<section class="hedron-component-demo" data-hedron-component-demo="FormField"><div class="hdc-stage"><div class="hdc-form"><label for="demo-email">Email address <b>Required</b></label><input id="demo-email" type="email" aria-describedby="demo-email-help"><small id="demo-email-help">We only use this for receipts.</small></div></div></section>

The preview is intentionally small enough to inspect with a keyboard and screen reader. It demonstrates the component's semantic result, not a screenshot. If the example represents HTMX activity, the “Simulated HTMX” trace confirms that documentation JavaScript supplied the response locally.

## Basic use

```python
from hedron import FormField, TextInput

component = FormField(name='email', label='Email address', control=TextInput('email', type='email'), help='We only use this for receipts.', required=True)
```

In a route, return the component inside a `Page`, or return it directly as a fragment through the framework adapter. Components are immutable descriptions of output: construct the complete state on the server and let the renderer serialize it.

## How it works

The component copies compatible controls before binding IDs and ARIA attributes, so shared component instances are not mutated. The bound component remains in the normal renderer tree and therefore keeps validation, identity tracking, diagnostics, and nesting behavior. Help and error nodes receive collision-free IDs and are connected with `aria-describedby`; pass `id=` when tests or external markup require a fixed value.

This component's core behavior is server-rendered HTML and does not require a browser runtime. The preview is ordinary semantic HTML, so keyboard, form, link, and disclosure behavior comes from the platform.

The component participates in Hedron's normal escaping, URL, and attribute validation. Values are data unless an API explicitly requires `SafeUrl` or reviewed `TrustedHtml`; do not pre-escape strings and do not concatenate HTML.

## Constructor and parameters

```python
FormField(*, name, label, control, id=None, help=None, required=False, error=None)
```

| Parameter | Type | Meaning |
|---|---|---|
| `name` | `str` | Stable field key used to derive IDs. |
| `label` | `str` | Visible label. |
| `control` | `NodeLike` | Required control slot. |
| `id` | `str | None` | Optional explicit control ID; otherwise a collision-free request-local ID is generated. |
| `help` | `str | None` | Associated instructions. |
| `required` | `bool` | Required state propagated to compatible controls. |
| `error` | `str | None` | Associated inline error. |

Keyword defaults are chosen for a safe, progressively enhanced baseline. Pass stable IDs when another component, a label, a URL fragment, a test, or an HTMX target must address the rendered node. Prefer typed component composition over hand-built HTML strings.

## Composition and backend behavior

Use `FormField` at the smallest level that owns its semantics. Page routes normally compose it under `Page`, `Main`, and an explicit heading structure. HTMX routes should return only the component region being replaced and should preserve stable target IDs across success, validation, empty, loading, and error responses.

When a request can mutate data, use POST, validate CSRF, authenticate and authorize on the server, validate typed input again, and return a bounded fragment. GET interactions must remain safe and repeatable. Native links and forms should still reach a useful server response when HTMX is unavailable.

## Accessibility

Write errors as actionable corrections and keep instructions available before an error occurs.

Test the demo and your application with keyboard-only input, visible focus, zoom, reduced motion, and at least one screen reader. Never make color, position, animation, or an icon the only carrier of state. Dynamic results need an appropriate status or alert and a deliberate focus strategy.

## Security and validation

Treat all request data, database content, filenames, URLs, labels, chart data, and Markdown as untrusted until the owning boundary validates it. Hedron escapes text and constrains dangerous surfaces, but it cannot decide application authorization or data exposure. Keep responses bounded, redact secrets before rendering, and use the narrowest URL and trust types available.

## Common mistakes

- Use the same `name` on the field and its control; avoid hand-authoring conflicting IDs.
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

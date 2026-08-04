---
title: TextInput
description: Collect a single line of typed text using a constrained input type.
---

# `TextInput`

Collect a single line of typed text using a constrained input type.

| | |
|---|---|
| Import | `from hedron import TextInput` |
| Distribution | `hedron` |
| Backend activity | No |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

<section class="hedron-component-demo" data-hedron-component-demo="TextInput"><div class="hdc-stage"><div class="hdc-form"><label for="demo-text">Email</label><input id="demo-text" type="email" autocomplete="email" placeholder="ada@example.com"></div></div></section>

The preview is intentionally small enough to inspect with a keyboard and screen reader. It demonstrates the component's semantic result, not a screenshot. If the example represents HTMX activity, the “Simulated HTMX” trace confirms that documentation JavaScript supplied the response locally.

## Basic use

```python
from hedron import TextInput

component = TextInput('email', type='email', autocomplete='email', required=True)
```

In a route, return the component inside a `Page`, or return it directly as a fragment through the framework adapter. Components are immutable descriptions of output: construct the complete state on the server and let the renderer serialize it.

## How it works

TextInput uses native constraints and preserves a supplied value during validation re-renders. The finite type set avoids accidentally exposing unsafe or poorly supported input modes.

This component's core behavior is server-rendered HTML and does not require a browser runtime. The preview is ordinary semantic HTML, so keyboard, form, link, and disclosure behavior comes from the platform.

The component participates in Hedron's normal escaping, URL, and attribute validation. Values are data unless an API explicitly requires `SafeUrl` or reviewed `TrustedHtml`; do not pre-escape strings and do not concatenate HTML.

## Constructor and parameters

```python
TextInput(name, *, id=None, value='', placeholder=None, required=False, type='text', autocomplete=None, disabled=False)
```

| Parameter | Type | Meaning |
|---|---|---|
| `name` | `str` | Submitted field name. |
| `id` | `str | None` | Control ID; defaults from name. |
| `value` | `str` | Current value for re-rendering. |
| `placeholder` | `str | None` | Optional hint. |
| `required` | `bool` | Native required constraint. |
| `type` | `text | email | password | search | tel | url` | Constrained browser input mode. |
| `autocomplete` | `str | None` | Browser autofill token. |
| `disabled` | `bool` | Disable and omit from submission. |

Keyword defaults are chosen for a safe, progressively enhanced baseline. Pass stable IDs when another component, a label, a URL fragment, a test, or an HTMX target must address the rendered node. Prefer typed component composition over hand-built HTML strings.

## Composition and backend behavior

Use `TextInput` at the smallest level that owns its semantics. Page routes normally compose it under `Page`, `Main`, and an explicit heading structure. HTMX fragment routes should return only the region being replaced and keep stable target IDs across success, validation, empty, loading, and error responses.

This component is primarily presentational; keep any mutation on an explicit action or component route.

## Accessibility

Provide a Label or FormField and use an accurate autocomplete token to help keyboard and assistive-technology users.

Verify keyboard use, visible focus, zoom, and reduced motion for interactive states. Prefer native semantics and status/alert announcements over color-only cues.

## Security and validation

Escape and trust-boundary types (`SafeUrl`, `TrustedHtml`) remain framework concerns; authorization and data exposure remain yours. Redact secrets before rendering.

## Common mistakes

- Never echo passwords back through `value`, and remember disabled controls are not submitted.
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

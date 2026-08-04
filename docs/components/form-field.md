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

Use `FormField` at the smallest level that owns its semantics. Page routes normally compose it under `Page`, `Main`, and an explicit heading structure. HTMX fragment routes should return only the region being replaced and keep stable target IDs across success, validation, empty, loading, and error responses.

This component is primarily presentational; keep any mutation on an explicit action or component route.

## Accessibility

Write errors as actionable corrections and keep instructions available before an error occurs.

Verify keyboard use, visible focus, zoom, and reduced motion for interactive states. Prefer native semantics and status/alert announcements over color-only cues.

## Security and validation

Escape and trust-boundary types (`SafeUrl`, `TrustedHtml`) remain framework concerns; authorization and data exposure remain yours. Redact secrets before rendering.

## Common mistakes

- Use the same `name` on the field and its control; avoid hand-authoring conflicting IDs.
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

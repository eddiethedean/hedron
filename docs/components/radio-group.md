---
title: RadioGroup
description: Choose exactly one option from a labelled set.
---

# `RadioGroup`

Choose exactly one option from a labelled set.

| | |
|---|---|
| Import | `from hedron import RadioGroup` |
| Distribution | `hedron` |
| Backend activity | No |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

<section class="hedron-component-demo" data-hedron-component-demo="RadioGroup"><div class="hdc-stage"><fieldset class="hdc-choices"><legend>Billing plan</legend><label><input type="radio" name="demo-plan" checked> Free</label><label><input type="radio" name="demo-plan"> Pro</label></fieldset></div></section>

The preview is intentionally small enough to inspect with a keyboard and screen reader. It demonstrates the component's semantic result, not a screenshot. If the example represents HTMX activity, the “Simulated HTMX” trace confirms that documentation JavaScript supplied the response locally.

## Basic use

```python
from hedron import RadioGroup

component = RadioGroup('plan', 'Billing plan', [('free', 'Free'), ('pro', 'Pro')], value='free')
```

In a route, return the component inside a `Page`, or return it directly as a fragment through the framework adapter. Components are immutable descriptions of output: construct the complete state on the server and let the renderer serialize it.

## How it works

A native fieldset and legend name the group; every option gets a collision-free ID, shared name, value, and associated label. Pass `id=` only when outside markup must use a predictable prefix.

This component's core behavior is server-rendered HTML and does not require a browser runtime. The preview is ordinary semantic HTML, so keyboard, form, link, and disclosure behavior comes from the platform.

The component participates in Hedron's normal escaping, URL, and attribute validation. Values are data unless an API explicitly requires `SafeUrl` or reviewed `TrustedHtml`; do not pre-escape strings and do not concatenate HTML.

## Constructor and parameters

```python
RadioGroup(name, legend, options, *, id=None, value=None, required=False)
```

| Parameter | Type | Meaning |
|---|---|---|
| `name` | `str` | Shared submitted field name. |
| `legend` | `str` | Group label. |
| `options` | `Sequence[tuple[str, str]]` | Value/label pairs. |
| `id` | `str | None` | Optional option-ID prefix; generated collision-free by default. |
| `value` | `str | None` | Selected option. |
| `required` | `bool` | Require one selection. |

Keyword defaults are chosen for a safe, progressively enhanced baseline. Pass stable IDs when another component, a label, a URL fragment, a test, or an HTMX target must address the rendered node. Prefer typed component composition over hand-built HTML strings.

## Composition and backend behavior

Use `RadioGroup` at the smallest level that owns its semantics. Page routes normally compose it under `Page`, `Main`, and an explicit heading structure. HTMX fragment routes should return only the region being replaced and keep stable target IDs across success, validation, empty, loading, and error responses.

This component is primarily presentational; keep any mutation on an explicit action or component route.

## Accessibility

Keep option labels parallel and make the legend a complete question or category.

Verify keyboard use, visible focus, zoom, and reduced motion for interactive states. Prefer native semantics and status/alert announcements over color-only cues.

## Security and validation

Escape and trust-boundary types (`SafeUrl`, `TrustedHtml`) remain framework concerns; authorization and data exposure remain yours. Redact secrets before rendering.

## Common mistakes

- Use Select when the option set is long or screen space is constrained.
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

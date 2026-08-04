---
title: AutoForm
description: Generate a labelled form from a typed FormModel and optionally submit it through HTMX.
---

# `AutoForm`

Generate a labelled form from a typed FormModel and optionally submit it through HTMX.

| | |
|---|---|
| Import | `from hedron import AutoForm` |
| Distribution | `hedron` |
| Backend activity | On submit |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

<section class="hedron-component-demo" data-hedron-component-demo="AutoForm"><div class="hdc-stage"><form class="hdc-form" data-hdc-form><label>Email address<input name="email" type="email" required placeholder="ada@example.com"></label><button class="hdc-button hdc-primary" type="submit">Submit</button></form><p role="status" aria-live="polite" data-hdc-status>Nothing submitted yet.</p></div><div class="hdc-request" data-hdc-request hidden><span>Simulated HTMX</span><code>GET /fragment → 200</code></div></section>

The preview is intentionally small enough to inspect with a keyboard and screen reader. It demonstrates the component's semantic result, not a screenshot. If the example represents HTMX activity, the “Simulated HTMX” trace confirms that documentation JavaScript supplied the response locally.

## Basic use

```python
from hedron import AutoForm

component = AutoForm(InviteMember, action='/team/invite', csrf_token=token, target='#invite-result', submit_label='Send invite')
```

In a route, return the component inside a `Page`, or return it directly as a fragment through the framework adapter. Components are immutable descriptions of output: construct the complete state on the server and let the renderer serialize it.

## How it works

AutoForm derives field labels and required state from model metadata, adds error and CSRF nodes, and uses normal form submission as its baseline. When `target` is set it emits the corresponding HTMX method, target, innerHTML swap, and duplicate-submit synchronization.

This component can initiate or represent a backend interaction. The live documentation intercepts that interaction with JavaScript and shows the same pending, success, or replacement states without making a real request. In an application, keep the URL, authorization, validation, and returned fragment on the server; JavaScript is only progressive enhancement.

The component participates in Hedron's normal escaping, URL, and attribute validation. Values are data unless an API explicitly requires `SafeUrl` or reviewed `TrustedHtml`; do not pre-escape strings and do not concatenate HTML.

## Constructor and parameters

```python
AutoForm(model, *, action, method='post', csrf_token=None, values=None, errors=(), submit_label='Submit', target=None)
```

| Parameter | Type | Meaning |
|---|---|---|
| `model` | `type[FormModel] | FormModel` | Field schema or populated instance. |
| `action` | `SafeUrl | str` | Validated endpoint. |
| `method` | `str` | GET or POST behavior. |
| `csrf_token` | `str | None` | Hidden CSRF value for state changes. |
| `values` | `Mapping` | Values restored after validation. |
| `errors` | `Sequence[str]` | Form-level errors. |
| `submit_label` | `str` | Primary action label. |
| `target` | `safe CSS selector | None` | HTMX response target. |

Keyword defaults are chosen for a safe, progressively enhanced baseline. Pass stable IDs when another component, a label, a URL fragment, a test, or an HTMX target must address the rendered node. Prefer typed component composition over hand-built HTML strings.

## Composition and backend behavior

Use `AutoForm` at the smallest level that owns its semantics. Page routes normally compose it under `Page`, `Main`, and an explicit heading structure. HTMX routes should return only the component region being replaced and should preserve stable target IDs across success, validation, empty, loading, and error responses.

When a request can mutate data, use POST, validate CSRF, authenticate and authorize on the server, validate typed input again, and return a bounded fragment. GET interactions must remain safe and repeatable. Native links and forms should still reach a useful server response when HTMX is unavailable.

## Accessibility

Review generated labels and add model titles that make domain-specific fields understandable.

Test the demo and your application with keyboard-only input, visible focus, zoom, reduced motion, and at least one screen reader. Never make color, position, animation, or an icon the only carrier of state. Dynamic results need an appropriate status or alert and a deliberate focus strategy.

## Security and validation

Treat all request data, database content, filenames, URLs, labels, chart data, and Markdown as untrusted until the owning boundary validates it. Hedron escapes text and constrains dangerous surfaces, but it cannot decide application authorization or data exposure. Keep responses bounded, redact secrets before rendering, and use the narrowest URL and trust types available.

## Common mistakes

- Generation does not replace authorization, CSRF validation, or server-side model validation.
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

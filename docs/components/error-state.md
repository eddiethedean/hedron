---
title: ErrorState
description: Present a recoverable request failure and optional HTMX retry.
---

# `ErrorState`

Present a recoverable request failure and optional HTMX retry.

| | |
|---|---|
| Import | `from hedron import ErrorState` |
| Distribution | `hedron` |
| Backend activity | On retry |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

<section class="hedron-component-demo" data-hedron-component-demo="ErrorState"><div class="hdc-stage"><div class="hdc-error" role="group" data-hdc-error><p role="alert">Activity could not be loaded.</p><button class="hdc-button" type="button" data-hdc-action="retry">Retry</button></div></div><div class="hdc-request" data-hdc-request hidden><span>Simulated HTMX</span><code>GET /fragment → 200</code></div></section>

The preview is intentionally small enough to inspect with a keyboard and screen reader. It demonstrates the component's semantic result, not a screenshot. If the example represents HTMX activity, the “Simulated HTMX” trace confirms that documentation JavaScript supplied the response locally.

## Basic use

```python
from hedron import ErrorState

component = ErrorState('Activity could not be loaded.', retry_href='/activity', target='#activity')
```

In a route, return the component inside a `Page`, or return it directly as a fragment through the framework adapter. Components are immutable descriptions of output: construct the complete state on the server and let the renderer serialize it.

## How it works

The error message uses alert semantics. When a retry URL is provided, the button issues a GET and replaces the target's outer HTML, allowing the server to restore the complete component state.

This component can initiate or represent a backend interaction. The live documentation intercepts that interaction with JavaScript and shows the same pending, success, or replacement states without making a real request. In an application, keep the URL, authorization, validation, and returned fragment on the server; JavaScript is only progressive enhancement.

The component participates in Hedron's normal escaping, URL, and attribute validation. Values are data unless an API explicitly requires `SafeUrl` or reviewed `TrustedHtml`; do not pre-escape strings and do not concatenate HTML.

## Constructor and parameters

```python
ErrorState(message, *, retry_href=None, retry_label='Retry', target=None)
```

| Parameter | Type | Meaning |
|---|---|---|
| `message` | `str` | Human-readable failure. |
| `retry_href` | `str | None` | Safe GET retry endpoint. |
| `retry_label` | `str` | Retry command. |
| `target` | `safe CSS selector | None` | Replacement target. |

Keyword defaults are chosen for a safe, progressively enhanced baseline. Pass stable IDs when another component, a label, a URL fragment, a test, or an HTMX target must address the rendered node. Prefer typed component composition over hand-built HTML strings.

## Composition and backend behavior

Use `ErrorState` at the smallest level that owns its semantics. Page routes normally compose it under `Page`, `Main`, and an explicit heading structure. HTMX fragment routes should return only the region being replaced and keep stable target IDs across success, validation, empty, loading, and error responses.

Mutating flows must use POST, validate CSRF, authorize on the server, re-validate typed input, and return a bounded fragment. GET remains safe and repeatable; native submit should still work without HTMX.

## Accessibility

Explain what failed, preserve user input, and make the next action explicit.

Verify keyboard use, visible focus, zoom, and reduced motion for interactive states. Prefer native semantics and status/alert announcements over color-only cues.

## Security and validation

Escape and trust-boundary types (`SafeUrl`, `TrustedHtml`) remain framework concerns; authorization and data exposure remain yours. Redact secrets before rendering.

## Common mistakes

- Do not reveal internal exceptions, stack traces, identifiers, or secrets in the message.
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

---
title: Poll
description: Refresh a fragment at a bounded interval while it remains in the DOM.
---

# `Poll`

Refresh a fragment at a bounded interval while it remains in the DOM.

| | |
|---|---|
| Import | `from hedron import Poll` |
| Distribution | `hedron` |
| Backend activity | On every interval |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

<section class="hedron-component-demo" data-hedron-component-demo="Poll"><div class="hdc-stage"><div class="hdc-result"><strong data-hdc-poll-state>Queued</strong><span data-hdc-poll-detail>Waiting for a worker</span></div><button class="hdc-button" type="button" data-hdc-action="poll">Start simulated polling</button></div><div class="hdc-request" data-hdc-request hidden><span>Simulated HTMX</span><code>GET /fragment → 200</code></div></section>

The preview is intentionally small enough to inspect with a keyboard and screen reader. It demonstrates the component's semantic result, not a screenshot. If the example represents HTMX activity, the “Simulated HTMX” trace confirms that documentation JavaScript supplied the response locally.

## Basic use

```python
from hedron import Poll, Status

component = Poll(ref=app.ref('job-status', job_id=job.id), interval_ms=2000, content=Status('Queued'))
```

In a route, return the component inside a `Page`, or return it directly as a fragment through the framework adapter. Components are immutable descriptions of output: construct the complete state on the server and let the renderer serialize it.

## How it works

HTMX's `every Nms` trigger refreshes the component into its collision-free self-target. Repeated instances can share one ComponentRef safely. Stop polling by returning replacement markup without the polling attributes once the terminal state is reached.

This component can initiate or represent a backend interaction. The live documentation intercepts that interaction with JavaScript and shows the same pending, success, or replacement states without making a real request. In an application, keep the URL, authorization, validation, and returned fragment on the server; JavaScript is only progressive enhancement.

The component participates in Hedron's normal escaping, URL, and attribute validation. Values are data unless an API explicitly requires `SafeUrl` or reviewed `TrustedHtml`; do not pre-escape strings and do not concatenate HTML.

## Constructor and parameters

```python
Poll(*, ref, interval_ms=5000, target_id=None, content=None)
```

| Parameter | Type | Meaning |
|---|---|---|
| `ref` | `ComponentRef` | Typed polling endpoint. |
| `interval_ms` | `int` | Interval, clamped to at least 250 ms. |
| `target_id` | `str | None` | Explicit self-target ID; generated collision-free by default. |
| `content` | `NodeLike | None` | Initial content. |

Keyword defaults are chosen for a safe, progressively enhanced baseline. Pass stable IDs when another component, a label, a URL fragment, a test, or an HTMX target must address the rendered node. Prefer typed component composition over hand-built HTML strings.

## Composition and backend behavior

Use `Poll` at the smallest level that owns its semantics. Page routes normally compose it under `Page`, `Main`, and an explicit heading structure. HTMX fragment routes should return only the region being replaced and keep stable target IDs across success, validation, empty, loading, and error responses.

Mutating flows must use POST, validate CSRF, authorize on the server, re-validate typed input, and return a bounded fragment. GET remains safe and repeatable; native submit should still work without HTMX.

## Accessibility

Announce only meaningful state transitions; announcing every timer tick overwhelms screen-reader users.

Verify keyboard use, visible focus, zoom, and reduced motion for interactive states. Prefer native semantics and status/alert announcements over color-only cues.

## Security and validation

Escape and trust-boundary types (`SafeUrl`, `TrustedHtml`) remain framework concerns; authorization and data exposure remain yours. Redact secrets before rendering.

## Common mistakes

- Use conservative intervals, private caching where appropriate, and a terminal response that stops server load.
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

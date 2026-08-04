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

Use `Poll` at the smallest level that owns its semantics. Page routes normally compose it under `Page`, `Main`, and an explicit heading structure. HTMX routes should return only the component region being replaced and should preserve stable target IDs across success, validation, empty, loading, and error responses.

When a request can mutate data, use POST, validate CSRF, authenticate and authorize on the server, validate typed input again, and return a bounded fragment. GET interactions must remain safe and repeatable. Native links and forms should still reach a useful server response when HTMX is unavailable.

## Accessibility

Announce only meaningful state transitions; announcing every timer tick overwhelms screen-reader users.

Test the demo and your application with keyboard-only input, visible focus, zoom, reduced motion, and at least one screen reader. Never make color, position, animation, or an icon the only carrier of state. Dynamic results need an appropriate status or alert and a deliberate focus strategy.

## Security and validation

Treat all request data, database content, filenames, URLs, labels, chart data, and Markdown as untrusted until the owning boundary validates it. Hedron escapes text and constrains dangerous surfaces, but it cannot decide application authorization or data exposure. Keep responses bounded, redact secrets before rendering, and use the narrowest URL and trust types available.

## Common mistakes

- Use conservative intervals, private caching where appropriate, and a terminal response that stops server load.
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

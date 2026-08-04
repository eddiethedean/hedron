---
title: ChatMessage
description: Render one typed, escaped item in an application-owned chat transcript.
---

# `ChatMessage`

Render one typed, escaped item in an application-owned chat transcript.

| | |
|---|---|
| Import | `from hedron import ChatMessage` |
| Distribution | `hedron` |
| Backend activity | No |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

<section class="hedron-component-demo" data-hedron-component-demo="ChatMessage"><div class="hdc-stage"><section class="hdc-chat" aria-label="Deployment conversation"><div class="hdc-transcript" role="log"><article class="hdc-chat-message hdc-chat-user"><strong>You</strong><p>Is the release ready?</p></article><article class="hdc-chat-message hdc-chat-assistant"><strong>Assistant</strong><p>Your deployment is ready.</p><small role="status" aria-live="polite">Delivered</small></article></div></section></div></section>

The preview is intentionally small enough to inspect with a keyboard and screen reader. It demonstrates the component's semantic result, not a screenshot. If the example represents HTMX activity, the “Simulated HTMX” trace confirms that documentation JavaScript supplied the response locally.

## Basic use

```python
from hedron import ChatMessage

component = ChatMessage('Your deployment is ready.', role='assistant', message_id='message-42', status='Delivered')
```

In a route, return the component inside a `Page`, or return it directly as a fragment through the framework adapter. Components are immutable descriptions of output: construct the complete state on the server and let the renderer serialize it.

## How it works

ChatMessage emits an article with role-specific classes and data metadata. A `status` message role becomes a polite live region; the separate status field also renders politely. History, ordering, retention, model-provider state, and streaming boundaries remain application-owned.

This component's core behavior is server-rendered HTML and does not require a browser runtime. The preview is ordinary semantic HTML, so keyboard, form, link, and disclosure behavior comes from the platform.

The component participates in Hedron's normal escaping, URL, and attribute validation. Values are data unless an API explicitly requires `SafeUrl` or reviewed `TrustedHtml`; do not pre-escape strings and do not concatenate HTML.

## Constructor and parameters

```python
ChatMessage(content, *, role='assistant', message_id=None, status=None)
```

| Parameter | Type | Meaning |
|---|---|---|
| `content` | `str` | Escaped message text. |
| `role` | `user | assistant | system | tool | status` | Typed speaker or message role. |
| `message_id` | `str | None` | Stable transcript item ID. |
| `status` | `str | None` | Optional polite delivery or streaming status. |

Keyword defaults are chosen for a safe, progressively enhanced baseline. Pass stable IDs when another component, a label, a URL fragment, a test, or an HTMX target must address the rendered node. Prefer typed component composition over hand-built HTML strings.

## Composition and backend behavior

Use `ChatMessage` at the smallest level that owns its semantics. Page routes normally compose it under `Page`, `Main`, and an explicit heading structure. HTMX routes should return only the component region being replaced and should preserve stable target IDs across success, validation, empty, loading, and error responses.

When a request can mutate data, use POST, validate CSRF, authenticate and authorize on the server, validate typed input again, and return a bounded fragment. GET interactions must remain safe and repeatable. Native links and forms should still reach a useful server response when HTMX is unavailable.

## Accessibility

Label the transcript itself, preserve meaningful DOM order, identify speakers with text rather than color alone, and avoid announcing the entire transcript when one status changes.

Test the demo and your application with keyboard-only input, visible focus, zoom, reduced motion, and at least one screen reader. Never make color, position, animation, or an icon the only carrier of state. Dynamic results need an appropriate status or alert and a deliberate focus strategy.

## Security and validation

Treat all request data, database content, filenames, URLs, labels, chart data, and Markdown as untrusted until the owning boundary validates it. Hedron escapes text and constrains dangerous surfaces, but it cannot decide application authorization or data exposure. Keep responses bounded, redact secrets before rendering, and use the narrowest URL and trust types available.

## Common mistakes

- Do not render secrets, hidden model instructions, tool credentials, or unbounded token streams as message content.
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

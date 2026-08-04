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

<section class="hedron-component-demo" data-hedron-component-demo="ChatMessage"><div class="hdc-stage"><section class="hdc-chat" aria-label="Deployment conversation"><header class="hdc-chat-header"><span class="hdc-chat-avatar" aria-hidden="true">H</span><span><strong>Release assistant</strong><small><i aria-hidden="true"></i>Online</small></span></header><div class="hdc-transcript" role="log"><span class="hdc-chat-day">Today</span><article class="hdc-chat-message hdc-chat-user"><span class="hdc-chat-avatar" aria-hidden="true">Y</span><div><strong>You</strong><p>Is the release ready?</p><time datetime="14:31">2:31 PM</time></div></article><article class="hdc-chat-message hdc-chat-assistant"><span class="hdc-chat-avatar" aria-hidden="true">H</span><div><strong>Hedron</strong><p>Your deployment is ready. All checks passed.</p><time datetime="14:32">2:32 PM · Delivered</time></div></article></div></section></div></section>

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

Use `ChatMessage` at the smallest level that owns its semantics. Page routes normally compose it under `Page`, `Main`, and an explicit heading structure. HTMX fragment routes should return only the region being replaced and keep stable target IDs across success, validation, empty, loading, and error responses.

This component is primarily presentational; keep any mutation on an explicit action or component route.

## Accessibility

Label the transcript itself, preserve meaningful DOM order, identify speakers with text rather than color alone, and avoid announcing the entire transcript when one status changes.

Verify keyboard use, visible focus, zoom, and reduced motion for interactive states. Prefer native semantics and status/alert announcements over color-only cues.

## Security and validation

Escape and trust-boundary types (`SafeUrl`, `TrustedHtml`) remain framework concerns; authorization and data exposure remain yours. Redact secrets before rendering.

## Common mistakes

- Do not render secrets, hidden model instructions, tool credentials, or unbounded token streams as message content.
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

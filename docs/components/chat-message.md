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

The preview is a local docs simulation (not a running Hedron server). Interactive demos show a “Simulated HTMX” trace when applicable.

## Basic use

```python
from hedron import ChatMessage

component = ChatMessage('Your deployment is ready.', role='assistant', message_id='message-42', status='Delivered')
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

ChatMessage emits an article with role-specific classes and data metadata. A `status` message role becomes a polite live region; the separate status field also renders politely. History, ordering, retention, model-provider state, and streaming boundaries remain application-owned.

This component's core behavior is server-rendered HTML and does not require a browser runtime. The preview is ordinary semantic HTML, so keyboard, form, link, and disclosure behavior comes from the platform.

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

## Composition and backend behavior

Keep `ChatMessage` at the smallest semantic boundary. Fragment routes should return only
the replaced region and preserve stable target IDs across success, validation, empty,
loading, and error responses.

`ChatMessage` participates in interaction markup. Pair it with an explicit `@app.action` POST (and CSRF) when the control mutates state.

## Accessibility

Label the transcript itself, preserve meaningful DOM order, identify speakers with text rather than color alone, and avoid announcing the entire transcript when one status changes.

## Security

Escaping and `SafeUrl` / `TrustedHtml` are framework concerns; authorization and data
exposure remain application code. Redact secrets before rendering.

## Common mistakes

- Do not render secrets, hidden model instructions, tool credentials, or unbounded token streams as message content.
- Do not copy docs-preview JavaScript into an application server.

## Testing

```python
from hedron import RenderMode, render

result = render(component, mode=RenderMode.FRAGMENT)
assert result.html
assert not result.diagnostics
```

[All component demos](index.md) · [Built-in API](../api/BUILT_INS.md) · [Testing](../guides/testing.md)

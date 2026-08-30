---
title: ChatInput
description: Submit an explicit chat message and optionally an attachment to a typed HTMX target.
---

# `ChatInput`

Submit an explicit chat message and optionally an attachment to a typed HTMX target.

| | |
|---|---|
| Import | `from hedron import ChatInput` |
| Distribution | `hedron` |
| Backend activity | On submit |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

<section class="hedron-component-demo" data-hedron-component-demo="ChatInput"><div class="hdc-stage"><section class="hdc-chat" aria-label="Deployment copilot conversation"><header class="hdc-chat-header"><span class="hdc-chat-avatar" aria-hidden="true">H</span><span><strong>Deployment copilot</strong><small><i aria-hidden="true"></i>Online · simulated assistant</small></span></header><div class="hdc-transcript" id="demo-transcript" role="log" aria-live="polite" data-hdc-transcript><span class="hdc-chat-day">Today</span><article class="hdc-chat-message hdc-chat-assistant"><span class="hdc-chat-avatar" aria-hidden="true">H</span><div><strong>Hedron</strong><p>Your production deployment is ready. Want me to summarize the six completed checks?</p><time datetime="14:32">2:32 PM</time></div></article></div><div class="hdc-chat-prompts" aria-label="Suggested prompts"><span>Try asking</span><button type="button" data-hdc-prompt="Summarize the deployment checks">Summarize checks</button><button type="button" data-hdc-prompt="Show me the rollout risks">Review rollout risks</button></div><form class="hdc-chat-form" data-hdc-chat-form><label class="hdc-visually-hidden" for="hdc-chat-message">Message</label><div class="hdc-chat-composer"><textarea id="hdc-chat-message" name="message" rows="1" required placeholder="Ask about this deployment…"></textarea><div><span class="hdc-chat-hint">Enter to send · Shift+Enter for a new line</span><button class="hdc-chat-send" type="submit"><span>Send</span><svg viewBox="0 0 20 20" aria-hidden="true"><path d="m3 3 14 7-14 7 2.3-6L12 10 5.3 9 3 3Z"/></svg></button></div></div></form><p class="hdc-chat-status" role="status" data-hdc-status>Ready to send.</p></section></div><div class="hdc-request" data-hdc-request hidden><span>Simulated HTMX</span><code>GET /fragment → 200</code></div></section>

The preview is a local docs simulation (not a running Hedron server). Interactive demos show a “Simulated HTMX” trace when applicable.

## Basic use

```python
from hedron import ChatInput
component = ChatInput(action='/chat', target='#transcript', placeholder='Ask the assistant', submit_label='Send')
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

ChatInput renders a labelled, required textarea and submit button in a POST form. A typed ComponentRef or action supplies the HTMX request, the target selector is validated, and responses normally append to the transcript. The server owns authentication, CSRF, rate limits, attachment validation, persistence, and bounded streaming.

This component can initiate or represent a backend interaction. The live documentation intercepts that interaction with JavaScript and shows the same pending, success, or replacement states without making a real request. In an application, keep the URL, authorization, validation, and returned fragment on the server; JavaScript is only progressive enhancement.

## Constructor and parameters

```text
ChatInput(*, ref=None, action=None, target=None, swap='beforeend', placeholder='Message', submit_label='Send', name='message', include_attachments=False)
```

| Parameter | Type | Meaning |
|---|---|---|
| `ref` | `ComponentRef | None` | Preferred typed POST endpoint. |
| `action` | `str | None` | Fallback HTMX POST URL. |
| `target` | `safe CSS selector | None` | Transcript receiving the response. |
| `swap` | `str` | HTMX swap strategy; defaults to beforeend. |
| `placeholder` | `str` | Textarea hint. |
| `submit_label` | `str` | Visible send action. |
| `name` | `str` | Submitted message field name. |
| `include_attachments` | `bool` | Add a labelled file input. |

## Composition and backend behavior

Keep `ChatInput` at the smallest semantic boundary. Fragment routes should return only
the replaced region and preserve stable target IDs across success, validation, empty,
loading, and error responses.

Mutating flows must use POST, validate CSRF, authorize on the server, re-validate typed input, and return a bounded fragment. GET remains safe and repeatable; native submit should still work without HTMX.

## Accessibility

Keep the textarea label available, announce sending and failure states without repeating the transcript, and preserve the draft when a request fails.

## Security

Escaping and `SafeUrl` / `TrustedHtml` are framework concerns; authorization and data
exposure remain application code. Redact secrets before rendering.

## Common mistakes

- Do not enable attachments without server-side filename, MIME, size, malware, authorization, storage, and retention controls.
- Do not copy docs-preview JavaScript into an application server.

## Testing

```python
from hedron import RenderMode, render

result = render(component, mode=RenderMode.FRAGMENT)
assert result.html
assert not result.diagnostics
```

[All component demos](index.md) · [Built-in API](../api/BUILT_INS.md) · [Testing](../guides/testing.md)

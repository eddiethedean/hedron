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

The preview is intentionally small enough to inspect with a keyboard and screen reader. It demonstrates the component's semantic result, not a screenshot. If the example represents HTMX activity, the “Simulated HTMX” trace confirms that documentation JavaScript supplied the response locally.

## Basic use

```python
from hedron import ChatInput

component = ChatInput(action='/chat', target='#transcript', placeholder='Ask the assistant', submit_label='Send')
```

In a route, return the component inside a `Page`, or return it directly as a fragment through the framework adapter. Components are immutable descriptions of output: construct the complete state on the server and let the renderer serialize it.

## How it works

ChatInput renders a labelled, required textarea and submit button in a POST form. A typed ComponentRef or action supplies the HTMX request, the target selector is validated, and responses normally append to the transcript. The server owns authentication, CSRF, rate limits, attachment validation, persistence, and bounded streaming.

This component can initiate or represent a backend interaction. The live documentation intercepts that interaction with JavaScript and shows the same pending, success, or replacement states without making a real request. In an application, keep the URL, authorization, validation, and returned fragment on the server; JavaScript is only progressive enhancement.

The component participates in Hedron's normal escaping, URL, and attribute validation. Values are data unless an API explicitly requires `SafeUrl` or reviewed `TrustedHtml`; do not pre-escape strings and do not concatenate HTML.

## Constructor and parameters

```python
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

Keyword defaults are chosen for a safe, progressively enhanced baseline. Pass stable IDs when another component, a label, a URL fragment, a test, or an HTMX target must address the rendered node. Prefer typed component composition over hand-built HTML strings.

## Composition and backend behavior

Use `ChatInput` at the smallest level that owns its semantics. Page routes normally compose it under `Page`, `Main`, and an explicit heading structure. HTMX routes should return only the component region being replaced and should preserve stable target IDs across success, validation, empty, loading, and error responses.

When a request can mutate data, use POST, validate CSRF, authenticate and authorize on the server, validate typed input again, and return a bounded fragment. GET interactions must remain safe and repeatable. Native links and forms should still reach a useful server response when HTMX is unavailable.

## Accessibility

Keep the textarea label available, announce sending and failure states without repeating the transcript, and preserve the draft when a request fails.

Test the demo and your application with keyboard-only input, visible focus, zoom, reduced motion, and at least one screen reader. Never make color, position, animation, or an icon the only carrier of state. Dynamic results need an appropriate status or alert and a deliberate focus strategy.

## Security and validation

Treat all request data, database content, filenames, URLs, labels, chart data, and Markdown as untrusted until the owning boundary validates it. Hedron escapes text and constrains dangerous surfaces, but it cannot decide application authorization or data exposure. Keep responses bounded, redact secrets before rendering, and use the narrowest URL and trust types available.

## Common mistakes

- Do not enable attachments without server-side filename, MIME, size, malware, authorization, storage, and retention controls.
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

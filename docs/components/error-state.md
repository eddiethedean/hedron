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

The preview is a local docs simulation (not a running Hedron server). Interactive demos show a “Simulated HTMX” trace when applicable.

## Basic use

```python
from hedron import ErrorState

component = ErrorState('Activity could not be loaded.', retry_href='/activity', target='#activity')
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

The error message uses alert semantics. When a retry URL is provided, the button issues a GET and replaces the target's outer HTML, allowing the server to restore the complete component state.

This component can initiate or represent a backend interaction. The live documentation intercepts that interaction with JavaScript and shows the same pending, success, or replacement states without making a real request. In an application, keep the URL, authorization, validation, and returned fragment on the server; JavaScript is only progressive enhancement.

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

## Composition and backend behavior

Keep `ErrorState` at the smallest semantic boundary. Fragment routes should return only
the replaced region and preserve stable target IDs across success, validation, empty,
loading, and error responses.

Mutating flows must use POST, validate CSRF, authorize on the server, re-validate typed input, and return a bounded fragment. GET remains safe and repeatable; native submit should still work without HTMX.

## Accessibility

Explain what failed, preserve user input, and make the next action explicit.

## Security

Escaping and `SafeUrl` / `TrustedHtml` are framework concerns; authorization and data
exposure remain application code. Redact secrets before rendering.

## Common mistakes

- Do not reveal internal exceptions, stack traces, identifiers, or secrets in the message.
- Do not copy docs-preview JavaScript into an application server.

## Testing

```python
from hedron import RenderMode, render

result = render(component, mode=RenderMode.FRAGMENT)
assert result.html
assert not result.diagnostics
```

[All component demos](index.md) · [Built-in API](../api/BUILT_INS.md) · [Testing](../guides/testing.md)

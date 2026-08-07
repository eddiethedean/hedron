---
title: Toast
description: Render a polite, transient-looking status message.
---

# `Toast`

Render a polite, transient-looking status message.

| | |
|---|---|
| Import | `from hedron import Toast` |
| Distribution | `hedron` |
| Backend activity | No |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

<!-- hedron-sim:component-toast -->

The preview is a local docs simulation (not a running Hedron server). Interactive demos show a “Simulated HTMX” trace when applicable.

## Basic use

```python
from hedron import Toast

component = Toast('API key copied.', tone='success')
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

Toast emits a polite status region with a tone class. It does not include timing or dismissal behavior; the docs Show button simulates inserting the server-rendered toast into an application shell.

This component can initiate or represent a backend interaction. The live documentation intercepts that interaction with JavaScript and shows the same pending, success, or replacement states without making a real request. In an application, keep the URL, authorization, validation, and returned fragment on the server; JavaScript is only progressive enhancement.

## Constructor and parameters

```python
Toast(message, *, tone='info')
```

| Parameter | Type | Meaning |
|---|---|---|
| `message` | `str` | Escaped toast text. |
| `tone` | `info | success | warning | danger` | Visual token. |

## Composition and backend behavior

Keep `Toast` at the smallest semantic boundary. Fragment routes should return only
the replaced region and preserve stable target IDs across success, validation, empty,
loading, and error responses.

Mutating flows must use POST, validate CSRF, authorize on the server, re-validate typed input, and return a bounded fragment. GET remains safe and repeatable; native submit should still work without HTMX.

## Accessibility

If application JavaScript removes the toast, allow enough reading time, pause any timer on hover or focus, and preserve critical messages elsewhere.

## Security

Escaping and `SafeUrl` / `TrustedHtml` are framework concerns; authorization and data
exposure remain application code. Redact secrets before rendering.

## Common mistakes

- Never auto-dismiss errors that require a user decision, and do not expect a `dismissible` constructor option.
- Do not copy docs-preview JavaScript into an application server.

## Testing

```python
from hedron import RenderMode, render

result = render(component, mode=RenderMode.FRAGMENT)
assert result.html
assert not result.diagnostics
```

[All component demos](index.md) · [Built-in API](../api/BUILT_INS.md) · [Testing](../guides/testing.md)

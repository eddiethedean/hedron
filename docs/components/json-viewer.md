---
title: JSONViewer
description: Pretty-print bounded JSON-like data with recursive secret redaction.
---

# `JSONViewer`

Pretty-print bounded JSON-like data with recursive secret redaction.

| | |
|---|---|
| Import | `from hedron import JSONViewer` |
| Distribution | `hedron` |
| Backend activity | No |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

<section class="hedron-component-demo" data-hedron-component-demo="JSONViewer"><div class="hdc-stage"><pre class="hdc-code"><code>{
  "job": 42,
  "status": "complete",
  "token": "***"
}</code></pre></div></section>

The preview is a local docs simulation (not a running Hedron server). Interactive demos show a “Simulated HTMX” trace when applicable.

## Basic use

```python
from hedron import JSONViewer

component = JSONViewer({'job': 42, 'status': 'complete', 'token': 'redacted automatically'})
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

JSONViewer recursively redacts Secret instances and keys containing common secret, password, or token terms, limits list breadth and recursion depth, formats with indentation, and truncates final text.

This component's core behavior is server-rendered HTML and does not require a browser runtime. The preview is ordinary semantic HTML, so keyboard, form, link, and disclosure behavior comes from the platform.

## Constructor and parameters

```python
JSONViewer(value, *, max_chars=100_000)
```

| Parameter | Type | Meaning |
|---|---|---|
| `value` | `Any` | JSON-like value. |
| `max_chars` | `int` | Hard text bound. |

## Composition and backend behavior

Keep `JSONViewer` at the smallest semantic boundary. Fragment routes should return only
the replaced region and preserve stable target IDs across success, validation, empty,
loading, and error responses.

This component is primarily presentational; keep any mutation on an explicit action or component route.

## Accessibility

Introduce complex payloads and avoid forcing users to navigate huge trees in the primary task flow.

## Security

Escaping and `SafeUrl` / `TrustedHtml` are framework concerns; authorization and data
exposure remain application code. Redact secrets before rendering.

## Common mistakes

- Key-name redaction is defense in depth, not a complete data-loss-prevention system.
- Do not copy docs-preview JavaScript into an application server.

## Testing

```python
from hedron import RenderMode, render

result = render(component, mode=RenderMode.FRAGMENT)
assert result.html
assert not result.diagnostics
```

[All component demos](index.md) · [Built-in API](../api/BUILT_INS.md) · [Testing](../guides/testing.md)

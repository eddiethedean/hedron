---
title: CodeViewer
description: Inspect bounded, escaped source text with optional language metadata.
---

# `CodeViewer`

Inspect bounded, escaped source text with optional language metadata.

| | |
|---|---|
| Import | `from hedron import CodeViewer` |
| Distribution | `hedron` |
| Backend activity | No |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

<section class="hedron-component-demo" data-hedron-component-demo="CodeViewer"><div class="hdc-stage"><pre class="hdc-code"><code><span>from</span> hedron <span>import</span> Text

Text(<em>"Hello, Hedron"</em>)</code></pre></div></section>

The preview is a local docs simulation (not a running Hedron server). Interactive demos show a “Simulated HTMX” trace when applicable.

## Basic use

```python
from hedron import CodeViewer
component = CodeViewer('[tool.hedron]\nplugins = []', language='toml', max_chars=20_000)
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

CodeViewer truncates oversized content before rendering it in pre/code elements. It is an inspection surface, not an editor or executable sandbox.

This component's core behavior is server-rendered HTML and does not require a browser runtime. The preview is ordinary semantic HTML, so keyboard, form, link, and disclosure behavior comes from the platform.

## Constructor and parameters

```text
CodeViewer(code, *, language=None, max_chars=100_000)
```

| Parameter | Type | Meaning |
|---|---|---|
| `code` | `str` | Source text. |
| `language` | `str | None` | Language metadata. |
| `max_chars` | `int` | Hard display bound. |

## Composition and backend behavior

Keep `CodeViewer` at the smallest semantic boundary. Fragment routes should return only
the replaced region and preserve stable target IDs across success, validation, empty,
loading, and error responses.

`CodeViewer` is primarily presentational; keep any mutation on an explicit action or component route.

## Accessibility

Provide context for what the code represents and keep horizontal scrolling keyboard-accessible.

## Security

Escaping and `SafeUrl` / `TrustedHtml` are framework concerns; authorization and data
exposure remain application code. Redact secrets before rendering.

## Common mistakes

- Redact secrets before construction; truncation is not redaction.
- Do not copy docs-preview JavaScript into an application server.

## Testing

```python
from hedron import RenderMode, render

result = render(component, mode=RenderMode.FRAGMENT)
assert result.html
assert not result.diagnostics
```

[All component demos](index.md) · [Built-in API](../api/BUILT_INS.md) · [Testing](../guides/testing.md)

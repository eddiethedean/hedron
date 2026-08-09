---
title: CodeBlock
description: Display escaped preformatted code with an optional language hook.
---

# `CodeBlock`

Display escaped preformatted code with an optional language hook.

| | |
|---|---|
| Import | `from hedron import CodeBlock` |
| Distribution | `hedron` |
| Backend activity | No |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

<section class="hedron-component-demo" data-hedron-component-demo="CodeBlock"><div class="hdc-stage"><pre class="hdc-code"><code><span>from</span> hedron <span>import</span> Text

Text(<em>"Hello, Hedron"</em>)</code></pre></div></section>

The preview is a local docs simulation (not a running Hedron server). Interactive demos show a “Simulated HTMX” trace when applicable.

## Basic use

```python
from hedron import CodeBlock, Text

component = CodeBlock("from hedron import Text\nText('Hello')", language='python')
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

The output is a `pre` containing `code`; the language becomes a class hook but syntax highlighting is an asset-layer concern. Code is escaped, never interpreted as markup.

This component's core behavior is server-rendered HTML and does not require a browser runtime. The preview is ordinary semantic HTML, so keyboard, form, link, and disclosure behavior comes from the platform.

## Constructor and parameters

```python
CodeBlock(code, *, language=None)
```

| Parameter | Type | Meaning |
|---|---|---|
| `code` | `str` | Literal code to display. |
| `language` | `str | None` | Language class for a highlighter. |

## Composition and backend behavior

Keep `CodeBlock` at the smallest semantic boundary. Fragment routes should return only
the replaced region and preserve stable target IDs across success, validation, empty,
loading, and error responses.

`CodeBlock` is primarily presentational; keep any mutation on an explicit action or component route.

## Accessibility

Keep long lines scrollable and introduce large examples with prose describing their purpose.

## Security

Escaping and `SafeUrl` / `TrustedHtml` are framework concerns; authorization and data
exposure remain application code. Redact secrets before rendering.

## Common mistakes

- Do not pass secrets, tokens, or unredacted production payloads into documentation code blocks.
- Do not copy docs-preview JavaScript into an application server.

## Testing

```python
from hedron import RenderMode, render

result = render(component, mode=RenderMode.FRAGMENT)
assert result.html
assert not result.diagnostics
```

[All component demos](index.md) · [Built-in API](../api/BUILT_INS.md) · [Testing](../guides/testing.md)

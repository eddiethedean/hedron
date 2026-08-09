---
title: Dialogue
description: Multi-speaker transcript with accessible speaker labels and timing metadata.
---

# `Dialogue`

Multi-speaker transcript with accessible speaker labels and timing metadata.

| | |
|---|---|
| Import | `from hedron import Dialogue` |
| Distribution | `hedron` |
| Backend activity | No |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

<section class="hedron-component-demo" data-hedron-component-demo="Dialogue"><div class="hdc-stage"><div class="hdc-result"><strong>Dialogue</strong><span>Multi-speaker transcript with accessible speaker labels and timing metadata.</span></div></div></section>

The preview is a local docs simulation (not a running Hedron server). Interactive demos show a “Simulated HTMX” trace when applicable.

## Basic use

```python
from hedron import Dialogue

component = Dialogue([{'speaker': 'A', 'text': 'Hello', 'start_ms': 0, 'end_ms': 500}])
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

Phase 0.18 model-demo presentation. Speaker identity must not rely on color alone.

This component's core behavior is server-rendered HTML and does not require a browser runtime. The preview is ordinary semantic HTML, so keyboard, form, link, and disclosure behavior comes from the platform.

## Constructor and parameters

```python
Dialogue(turns, *, title='Dialogue', class_=None, mark=None)
```

| Parameter | Type | Meaning |
|---|---|---|
| `turns` | `Sequence[DialogueTurn | Mapping]` | Ordered speaker turns with optional timing/tags. |
| `title` | `str` | Section label. |
| `mark` | `str | None` | Optional stable test mark (`data-hedron-mark`). |

## Composition and backend behavior

Keep `Dialogue` at the smallest semantic boundary. Fragment routes should return only
the replaced region and preserve stable target IDs across success, validation, empty,
loading, and error responses.

`Dialogue` is primarily presentational; keep any mutation on an explicit action or component route.

## Accessibility

Each turn exposes an accessible speaker label; timing/tags are text metadata.

## Security

Escaping and `SafeUrl` / `TrustedHtml` are framework concerns; authorization and data
exposure remain application code. Redact secrets before rendering.

## Common mistakes

- Do not use Dialogue as a chat input widget; pair with ChatMessage/ChatInput for interactive chat.
- Do not copy docs-preview JavaScript into an application server.

## Testing

```python
from hedron import RenderMode, render

result = render(component, mode=RenderMode.FRAGMENT)
assert result.html
assert not result.diagnostics
```

[All component demos](index.md) · [Built-in API](../api/BUILT_INS.md) · [Testing](../guides/testing.md)

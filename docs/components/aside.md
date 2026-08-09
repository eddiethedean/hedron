---
title: Aside
description: Render the semantic `aside` landmark for related but secondary content.
---

# `Aside`

Render the semantic `aside` landmark for related but secondary content.

| | |
|---|---|
| Import | `from hedron import Aside` |
| Distribution | `hedron` |
| Backend activity | No |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

<section class="hedron-component-demo" data-hedron-component-demo="Aside"><div class="hdc-stage"><aside class="hdc-landmark"><span>&lt;aside&gt;</span><strong>Aside content</strong><p>Render the semantic `aside` landmark for related but secondary content.</p></aside></div></section>

The preview is a local docs simulation (not a running Hedron server). Interactive demos show a “Simulated HTMX” trace when applicable.

## Basic use

```python
from hedron import Aside, Heading, Text

component = Aside(Heading('On this page', level=2), Text('Related settings'))
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

`Aside` emits a native `<aside>`, preserving semantic navigation instead of using a generic div. Children may be passed individually or as one non-string sequence. Landmark helpers are real typed classes with an allowlisted attribute set.

This component's core behavior is server-rendered HTML and does not require a browser runtime. The preview is ordinary semantic HTML, so keyboard, form, link, and disclosure behavior comes from the platform.

## Constructor and parameters

```python
Aside(*nodes, children=None, class_=None, id=None, lang=None, dir=None, role=None, aria=None, data=None, ...)
```

| Parameter | Type | Meaning |
|---|---|---|
| `nodes` | `NodeLike` | Positional content belonging to this semantic region. |
| `children` | `NodeLike | sequence | None` | Keyword alternative; combines with positional nodes. |
| `class_` | `str | None` | Optional authored class name. |
| `id` | `str | None` | Stable fragment or target identifier. |
| `lang / dir / role / title / tabindex / aria / data / hidden` | `allowlisted` | Safe HTML attributes; hostile roles like `presentation` / `none` are rejected. |

## Composition and backend behavior

Keep `Aside` at the smallest semantic boundary. Fragment routes should return only
the replaced region and preserve stable target IDs across success, validation, empty,
loading, and error responses.

`Aside` is primarily presentational; keep any mutation on an explicit action or component route.

## Accessibility

The aside should remain understandable as complementary content when read separately from the main flow.

## Security

Escaping and `SafeUrl` / `TrustedHtml` are framework concerns; authorization and data
exposure remain application code. Redact secrets before rendering.

## Common mistakes

- Do not place content required to complete the primary task only in an aside.
- Do not copy docs-preview JavaScript into an application server.

## Testing

```python
from hedron import RenderMode, render

result = render(component, mode=RenderMode.FRAGMENT)
assert result.html
assert not result.diagnostics
```

[All component demos](index.md) · [Built-in API](../api/BUILT_INS.md) · [Testing](../guides/testing.md)

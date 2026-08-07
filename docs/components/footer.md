---
title: Footer
description: Render the semantic `footer` landmark for closing information for a page or section.
---

# `Footer`

Render the semantic `footer` landmark for closing information for a page or section.

| | |
|---|---|
| Import | `from hedron import Footer` |
| Distribution | `hedron` |
| Backend activity | No |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

<section class="hedron-component-demo" data-hedron-component-demo="Footer"><div class="hdc-stage"><footer class="hdc-landmark"><span>&lt;footer&gt;</span><strong>Footer content</strong><p>Render the semantic `footer` landmark for closing information for a page or section.</p></footer></div></section>

The preview is a local docs simulation (not a running Hedron server). Interactive demos show a “Simulated HTMX” trace when applicable.

## Basic use

```python
from hedron import Footer, Heading, Text

component = Footer(Heading('Support', level=2), Text('Contact the platform team'))
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

`Footer` emits a native `<footer>`, preserving semantic navigation instead of using a generic div. Children may be passed individually or as one non-string sequence. Landmark helpers are real typed classes with an allowlisted attr set (`LANDMARK-019`).

This component's core behavior is server-rendered HTML and does not require a browser runtime. The preview is ordinary semantic HTML, so keyboard, form, link, and disclosure behavior comes from the platform.

## Constructor and parameters

```python
Footer(*nodes, children=None, class_=None, id=None, lang=None, dir=None, role=None, aria=None, data=None, ...)
```

| Parameter | Type | Meaning |
|---|---|---|
| `nodes` | `NodeLike` | Positional content belonging to this semantic region. |
| `children` | `NodeLike | sequence | None` | Keyword alternative; combines with positional nodes. |
| `class_` | `str | None` | Optional authored class name. |
| `id` | `str | None` | Stable fragment or target identifier. |
| `lang / dir / role / title / tabindex / aria / data / hidden` | `allowlisted` | Safe HTML attrs (`LANDMARK-019`); hostile roles like `presentation` / `none` are rejected. |

## Composition and backend behavior

Keep `Footer` at the smallest semantic boundary. Fragment routes should return only
the replaced region and preserve stable target IDs across success, validation, empty,
loading, and error responses.

This component is primarily presentational; keep any mutation on an explicit action or component route.

## Accessibility

Use explicit link text and keep legal or support navigation grouped meaningfully.

## Security

Escaping and `SafeUrl` / `TrustedHtml` are framework concerns; authorization and data
exposure remain application code. Redact secrets before rendering.

## Common mistakes

- A nested section footer is not the page-wide contentinfo landmark.
- Do not copy docs-preview JavaScript into an application server.

## Testing

```python
from hedron import RenderMode, render

result = render(component, mode=RenderMode.FRAGMENT)
assert result.html
assert not result.diagnostics
```

[All component demos](index.md) · [Built-in API](../api/BUILT_INS.md) · [Testing](../guides/testing.md)

---
title: Main
description: Render the semantic `main` landmark for the page's primary content.
---

# `Main`

Render the semantic `main` landmark for the page's primary content.

| | |
|---|---|
| Import | `from hedron import Main` |
| Distribution | `hedron` |
| Backend activity | No |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

<section class="hedron-component-demo" data-hedron-component-demo="Main"><div class="hdc-stage"><main class="hdc-landmark"><span>&lt;main&gt;</span><strong>Main content</strong><p>Render the semantic `main` landmark for the page's primary content.</p></main></div></section>

The preview is a local docs simulation (not a running Hedron server). Interactive demos show a “Simulated HTMX” trace when applicable.

## Basic use

```python
from hedron import Heading, Main, Text

component = Main(Heading('Dashboard', level=1), Text('Current workspace activity'))
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

`Main` emits a native `<main>`, preserving semantic navigation instead of using a generic div. Children may be passed individually or as one non-string sequence. Landmark helpers are real typed classes with an allowlisted attr set (`LANDMARK-019`).

This component's core behavior is server-rendered HTML and does not require a browser runtime. The preview is ordinary semantic HTML, so keyboard, form, link, and disclosure behavior comes from the platform.

## Constructor and parameters

```python
Main(*nodes, children=None, class_=None, id=None, lang=None, dir=None, role=None, aria=None, data=None, ...)
```

| Parameter | Type | Meaning |
|---|---|---|
| `nodes` | `NodeLike` | Positional content belonging to this semantic region. |
| `children` | `NodeLike | sequence | None` | Keyword alternative; combines with positional nodes. |
| `class_` | `str | None` | Optional authored class name. |
| `id` | `str | None` | Stable fragment or target identifier. |
| `lang / dir / role / title / tabindex / aria / data / hidden` | `allowlisted` | Safe HTML attrs (`LANDMARK-019`); hostile roles like `presentation` / `none` are rejected. |

## Composition and backend behavior

Keep `Main` at the smallest semantic boundary. Fragment routes should return only
the replaced region and preserve stable target IDs across success, validation, empty,
loading, and error responses.

This component is primarily presentational; keep any mutation on an explicit action or component route.

## Accessibility

Use one visible main landmark per full page so keyboard and screen-reader users can reach primary content directly.

## Security

Escaping and `SafeUrl` / `TrustedHtml` are framework concerns; authorization and data
exposure remain application code. Redact secrets before rendering.

## Common mistakes

- Do not put repeated navigation, footers, or modal content inside main.
- Do not copy docs-preview JavaScript into an application server.

## Testing

```python
from hedron import RenderMode, render

result = render(component, mode=RenderMode.FRAGMENT)
assert result.html
assert not result.diagnostics
```

[All component demos](index.md) · [Built-in API](../api/BUILT_INS.md) · [Testing](../guides/testing.md)

---
title: AppFooter
description: Typed application footer region for AppShell chrome.
---

# `AppFooter`

Typed application footer region for AppShell chrome.

| | |
|---|---|
| Import | `from hedron import AppFooter` |
| Distribution | `hedron` |
| Backend activity | No |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

<section class="hedron-component-demo" data-hedron-component-demo="AppFooter"><div class="hdc-stage"><footer class="hdc-muted"><span>© Acme</span> · <span>Support</span></footer></div></section>

The preview is a local docs simulation (not a running Hedron server). Interactive demos show a “Simulated HTMX” trace when applicable.

## Basic use

```python
from hedron import AppFooter, Text

component = AppFooter(Text('© Acme'), Text('Support'))
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

AppFooter provides a presentation-token footer without application CSS.

This component's core behavior is server-rendered HTML and does not require a browser runtime. The preview is ordinary semantic HTML, so keyboard, form, link, and disclosure behavior comes from the platform.

## Constructor and parameters

```python
AppFooter(*nodes, *, width=None, id=None, class_=None)
```

| Parameter | Type | Meaning |
|---|---|---|
| `nodes` | `NodeLike` | Footer body content. |
| `width` | `content | narrow | wide | full | None` | Optional content width token. |

## Composition and backend behavior

Keep `AppFooter` at the smallest semantic boundary. Fragment routes should return only
the replaced region and preserve stable target IDs across success, validation, empty,
loading, and error responses.

`AppFooter` is primarily presentational; keep any mutation on an explicit action or component route.

## Accessibility

Keep legal and support links keyboard-reachable.

## Security

Escaping and `SafeUrl` / `TrustedHtml` are framework concerns; authorization and data
exposure remain application code. Redact secrets before rendering.

## Common mistakes

- Do not place primary navigation exclusively in the footer.
- Do not copy docs-preview JavaScript into an application server.

## Testing

```python
from hedron import RenderMode, render

result = render(component, mode=RenderMode.FRAGMENT)
assert result.html
assert not result.diagnostics
```

[All component demos](index.md) · [Built-in API](../api/BUILT_INS.md) · [Testing](../guides/testing.md)

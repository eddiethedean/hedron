---
title: Link
description: Navigate with a validated internal or external anchor.
---

# `Link`

Navigate with a validated internal or external anchor.

| | |
|---|---|
| Import | `from hedron import Link` |
| Distribution | `hedron` |
| Backend activity | No |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

<section class="hedron-component-demo" data-hedron-component-demo="Link"><div class="hdc-stage"><div class="hdc-link-demo"><span class="hdc-eyebrow">Navigation</span><a href="#component-demo-result" data-hdc-local-link>View audit log →</a><p id="component-demo-result" class="hdc-muted">A real anchor preserves browser navigation behavior.</p></div></div></section>

The preview is a local docs simulation (not a running Hedron server). Interactive demos show a “Simulated HTMX” trace when applicable.

## Basic use

```python
from hedron import Link

component = Link('View audit log', '/audit')
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

URLs pass through Hedron's SafeUrl navigation policy. External links receive `target=_blank` and `rel=noopener noreferrer`; internal links remain ordinary same-context anchors and work without JavaScript.

This component's core behavior is server-rendered HTML and does not require a browser runtime. The preview is ordinary semantic HTML, so keyboard, form, link, and disclosure behavior comes from the platform.

## Constructor and parameters

```python
Link(label, href, *, external=False)
```

| Parameter | Type | Meaning |
|---|---|---|
| `label` | `str` | Visible link text. |
| `href` | `SafeUrl | str` | Validated navigation URL. |
| `external` | `bool` | Allow an external URL and open it defensively in a new tab. |

## Composition and backend behavior

Keep `Link` at the smallest semantic boundary. Fragment routes should return only
the replaced region and preserve stable target IDs across success, validation, empty,
loading, and error responses.

This component is primarily presentational; keep any mutation on an explicit action or component route.

## Accessibility

Link text should identify the destination out of context; tell users when a destination opens a different site or context if that is not obvious.

## Security

Escaping and `SafeUrl` / `TrustedHtml` are framework concerns; authorization and data
exposure remain application code. Redact secrets before rendering.

## Common mistakes

- Use LinkButton only for a navigation link that is intentionally styled like a button—do not turn a command into a fake link.
- Do not copy docs-preview JavaScript into an application server.

## Testing

```python
from hedron import RenderMode, render

result = render(component, mode=RenderMode.FRAGMENT)
assert result.html
assert not result.diagnostics
```

[All component demos](index.md) · [Built-in API](../api/BUILT_INS.md) · [Testing](../guides/testing.md)

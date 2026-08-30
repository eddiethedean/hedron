---
title: Icon
description: Trusted registry SVG with a bounded size vocabulary.
---

# `Icon`

Trusted registry SVG with a bounded size vocabulary.

| | |
|---|---|
| Import | `from hedron import Icon` |
| Distribution | `hedron` |
| Backend activity | No |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

<section class="hedron-component-demo" data-hedron-component-demo="Icon"><div class="hdc-stage"><div class="hdc-inline"><span class="hdc-badge hdc-success" role="img" aria-label="Complete">✓</span><span class="hdc-muted">Trusted registry icon · size md</span></div></div></section>

The preview is a local docs simulation (not a running Hedron server). Interactive demos show a “Simulated HTMX” trace when applicable.

## Basic use

```python
from hedron import Icon, register_first_party_icons
register_first_party_icons()

component = Icon('check', size='sm', title='Complete')
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

Icon fails closed on unknown names and never accepts raw SVG markup from application authors. Applications may opt into the small semantic pack with `register_first_party_icons()` and then use names such as `home`, `search`, `pipeline`, `check`, and `chevron-right`; directional icons mirror automatically under RTL.

This component's core behavior is server-rendered HTML and does not require a browser runtime. The preview is ordinary semantic HTML, so keyboard, form, link, and disclosure behavior comes from the platform.

## Constructor and parameters

```text
Icon(name, *, size='md', title=None, decorative=False, id=None, class_=None)
```

| Parameter | Type | Meaning |
|---|---|---|
| `name` | `str` | Registered icon name from the trusted registry. |
| `size` | `str` | Closed size vocabulary (`sm` / `md` / `lg` / …). |
| `title` | `str | None` | Accessible name override when not decorative. |
| `decorative` | `bool` | When true, hide the icon from the accessibility tree. |

## Composition and backend behavior

Keep `Icon` at the smallest semantic boundary. Fragment routes should return only
the replaced region and preserve stable target IDs across success, validation, empty,
loading, and error responses.

`Icon` is primarily presentational; keep any mutation on an explicit action or component route.

## Accessibility

Prefer decorative=True beside visible text; otherwise supply a title that names the meaning.

## Security

Escaping and `SafeUrl` / `TrustedHtml` are framework concerns; authorization and data
exposure remain application code. Redact secrets before rendering.

## Common mistakes

- Do not use Icon as a button—use IconButton for actionable controls.
- Do not copy docs-preview JavaScript into an application server.

## Testing

```python
from hedron import RenderMode, render

result = render(component, mode=RenderMode.FRAGMENT)
assert result.html
assert not result.diagnostics
```

[All component demos](index.md) · [Built-in API](../api/BUILT_INS.md) · [Testing](../guides/testing.md)

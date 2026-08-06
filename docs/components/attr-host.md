---
title: AttrHost
description: Stable element that can receive attribute-only OOB updates.
---

# `AttrHost`

Stable element that can receive attribute-only OOB updates.

| | |
|---|---|
| Import | `from hedron import AttrHost` |
| Distribution | `hedron` |
| Backend activity | No |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

<section class="hedron-component-demo" data-hedron-component-demo="AttrHost"><div class="hdc-stage"><div class="hdc-result"><strong>AttrHost</strong><span>Stable element that can receive attribute-only OOB updates.</span></div></div></section>

The preview is a local docs simulation (not a running Hedron server). Interactive demos show a “Simulated HTMX” trace when applicable.

## Basic use

```python
from hedron import AttrHost, Text

component = AttrHost(Text('Ready'), id='status-host', attrs={'data-state': 'idle'})
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

AttrHost is the companion to OobHost for attribute swaps (for example busy/disabled flags) without replacing the whole subtree.

This component's core behavior is server-rendered HTML and does not require a browser runtime. The preview is ordinary semantic HTML, so keyboard, form, link, and disclosure behavior comes from the platform.

## Constructor and parameters

```python
AttrHost(*nodes, *, id, tag='div', attrs=None, class_=None)
```

| Parameter | Type | Meaning |
|---|---|---|
| `id` | `str` | Required stable element id. |
| `attrs` | `mapping | None` | Initial attributes eligible for attr OOB patches. |
| `tag / class_` | `str` | Host element and optional classes. |

## Composition and backend behavior

Keep `AttrHost` at the smallest semantic boundary. Fragment routes should return only
the replaced region and preserve stable target IDs across success, validation, empty,
loading, and error responses.

This component is primarily presentational; keep any mutation on an explicit action or component route.

## Accessibility

Keep attribute names on an allowlist and authorize updates the same way as content OOB.

## Security

Escaping and `SafeUrl` / `TrustedHtml` are framework concerns; authorization and data
exposure remain application code. Redact secrets before rendering.

## Common mistakes

- Do not treat AttrHost as a general DOM mutation API.
- Do not copy docs-preview JavaScript into an application server.

## Testing

```python
from hedron import RenderMode, render

result = render(component, mode=RenderMode.FRAGMENT)
assert result.html
assert not result.diagnostics
```

[All component demos](index.md) · [Built-in API](../api/BUILT_INS.md) · [Testing](../guides/testing.md)

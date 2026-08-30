---
title: AmbientBackdrop
description: Finite decorative backdrop that remains inert and outside content semantics.
---

# `AmbientBackdrop`

Finite decorative backdrop that remains inert and outside content semantics.
!!! note "Phase 0.61 published surface"

    This additive contract is implemented and verified for the published 0.61.x Supported surface. See [RELEASE_0_61](https://github.com/eddiethedean/hedron/blob/main/docs/acceptance/RELEASE_0_61.md).


| | |
|---|---|
| Import | `from hedron import AmbientBackdrop` |
| Distribution | `hedron` |
| Backend activity | No |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

<section class="hedron-component-demo" data-hedron-component-demo="AmbientBackdrop"><div class="hdc-stage"><div class="hdc-result"><strong>AmbientBackdrop</strong><span>Finite decorative backdrop that remains inert and outside content semantics.</span></div></div></section>

The preview is a local docs simulation (not a running Hedron server). Interactive demos show a “Simulated HTMX” trace when applicable.

## Basic use

```python
from hedron import AmbientBackdrop, Container, Text
component = AmbientBackdrop(Container(Text('Dashboard'), max_width='lg'), pattern='mesh', tone='accent')
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

AmbientBackdrop emits an aria-hidden decoration layer with pointer-events disabled, so child content remains in document order. Print, forced-colors, and reduced-transparency styles hide the decoration.

This component's core behavior is server-rendered HTML and does not require a browser runtime. The preview is ordinary semantic HTML, so keyboard, form, link, and disclosure behavior comes from the platform.

## Constructor and parameters

```text
AmbientBackdrop(*nodes, pattern='radial', tone='accent', intensity='subtle', id=None, class_=None, mark=None)
```

| Parameter | Type | Meaning |
|---|---|---|
| `nodes / children` | `NodeLike` | Semantic page or surface content above the decoration. |
| `pattern` | `radial | dots | grid | mesh` | Finite deterministic decoration preset. |
| `tone` | `accent | muted | neutral` | Theme-owned decoration tone. |
| `intensity` | `subtle | soft` | Bounded contrast treatment. |

## Composition and backend behavior

Keep `AmbientBackdrop` at the smallest semantic boundary. Fragment routes should return only
the replaced region and preserve stable target IDs across success, validation, empty,
loading, and error responses.

`AmbientBackdrop` is primarily presentational; keep any mutation on an explicit action or component route.

## Accessibility

Keep meaningful headings, status, and focusable controls in the child content; the backdrop is never the source of contrast or information.

## Security

Escaping and `SafeUrl` / `TrustedHtml` are framework concerns; authorization and data
exposure remain application code. Redact secrets before rendering.

## Common mistakes

- Do not pass arbitrary gradients, CSS strings, or interactive content as decoration.
- Do not copy docs-preview JavaScript into an application server.

## Testing

```python
from hedron import RenderMode, render

result = render(component, mode=RenderMode.FRAGMENT)
assert result.html
assert not result.diagnostics
```

[All component demos](index.md) · [Built-in API](../api/BUILT_INS.md) · [Testing](../guides/testing.md)

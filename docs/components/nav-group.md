---
title: NavGroup
description: Standalone labelled navigation group shared by AppShell and fragment responses.
---

# `NavGroup`

Standalone labelled navigation group shared by AppShell and fragment responses.
!!! note "Phase 0.61 published surface"

    This additive contract is implemented and verified for the published 0.61.x Supported surface. See [RELEASE_0_61](https://github.com/eddiethedean/hedron/blob/main/docs/acceptance/RELEASE_0_61.md).


| | |
|---|---|
| Import | `from hedron import NavGroup` |
| Distribution | `hedron` |
| Backend activity | No |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

<section class="hedron-component-demo" data-hedron-component-demo="NavGroup"><div class="hdc-stage"><div class="hdc-result"><strong>NavGroup</strong><span>Standalone labelled navigation group shared by AppShell and fragment responses.</span></div></div></section>

The preview is a local docs simulation (not a running Hedron server). Interactive demos show a “Simulated HTMX” trace when applicable.

## Basic use

```python
from hedron import NavGroup, NavLink

component = NavGroup('Workspace', NavLink('Overview', '/'), NavLink('Reports', '/reports'))
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

A labelled NavGroup emits role=group, aria-label, a visible group label, and stable CSS/data hooks. AppShell nav_groups lowers through the same component.

This component's core behavior is server-rendered HTML and does not require a browser runtime. The preview is ordinary semantic HTML, so keyboard, form, link, and disclosure behavior comes from the platform.

## Constructor and parameters

```python
NavGroup(label=None, *items, children=None, id=None, class_=None, mark=None)
```

| Parameter | Type | Meaning |
|---|---|---|
| `label` | `str | None` | Visible and accessible group label; omit when the surrounding nav owns the name. |
| `items / children` | `NodeLike` | Links or other already-authorized navigation items. |

## Composition and backend behavior

Keep `NavGroup` at the smallest semantic boundary. Fragment routes should return only
the replaced region and preserve stable target IDs across success, validation, empty,
loading, and error responses.

`NavGroup` is primarily presentational; keep any mutation on an explicit action or component route.

## Accessibility

Keep the surrounding nav landmark labelled and preserve each item’s native focus and link behavior.

## Security

Escaping and `SafeUrl` / `TrustedHtml` are framework concerns; authorization and data
exposure remain application code. Redact secrets before rendering.

## Common mistakes

- Do not use NavGroup to bypass route authorization or nest competing nav landmarks.
- Do not copy docs-preview JavaScript into an application server.

## Testing

```python
from hedron import RenderMode, render

result = render(component, mode=RenderMode.FRAGMENT)
assert result.html
assert not result.diagnostics
```

[All component demos](index.md) · [Built-in API](../api/BUILT_INS.md) · [Testing](../guides/testing.md)

---
title: LinkButton
description: Navigate with an anchor styled as a prominent button.
---

# `LinkButton`

Navigate with an anchor styled as a prominent button.

| | |
|---|---|
| Import | `from hedron import LinkButton` |
| Distribution | `hedron` |
| Backend activity | No |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

<section class="hedron-component-demo" data-hedron-component-demo="LinkButton"><div class="hdc-stage"><div class="hdc-link-demo"><span class="hdc-eyebrow">Navigation</span><a class="hdc-button hdc-primary" href="#component-demo-result" data-hdc-local-link>Create account →</a><p id="component-demo-result" class="hdc-muted">A real anchor preserves browser navigation behavior.</p></div></div></section>

The preview is a local docs simulation (not a running Hedron server). Interactive demos show a “Simulated HTMX” trace when applicable.

## Basic use

```python
from hedron import LinkButton

component = LinkButton('Create account', '/signup', size='sm', width='full')
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

Despite its appearance, LinkButton is an anchor and preserves open-in-new-tab, copy-link, and no-JavaScript navigation behavior. Its 0.59 `size`, `width`, `appearance`, `emphasis`, and `attrs=` contract is aligned with `Button`.

This component's core behavior is server-rendered HTML and does not require a browser runtime. The preview is ordinary semantic HTML, so keyboard, form, link, and disclosure behavior comes from the platform.

## Constructor and parameters

```python
LinkButton(label, href, *, size=None, width=None, appearance=None, emphasis=None, id=None, class_=None, attrs=None)
```

| Parameter | Type | Meaning |
|---|---|---|
| `label` | `str` | Visible navigation label. |
| `href` | `SafeUrl | str` | Validated destination. |
| `size` | `sm | md | lg | None` | Shared control size marker. |
| `width` | `content | field | full | None` | Shared width intent. |
| `appearance` | `solid | outline | soft | ghost | plain | raised | None` | Treatment independent of meaning. |
| `emphasis` | `primary | secondary | danger | neutral | None` | Semantic meaning independent of treatment. |
| `attrs` | `Mapping[str, HtmlAttrValue] | None` | Validated global, ARIA, data, approved HTMX, and popover/dialog-trigger attributes. |

## Composition and backend behavior

Keep `LinkButton` at the smallest semantic boundary. Fragment routes should return only
the replaced region and preserve stable target IDs across success, validation, empty,
loading, and error responses.

`LinkButton` participates in interaction markup. Pair it with an explicit `@action` / `@component` POST (and CSRF) when the control mutates state.

## Accessibility

The label should describe the destination and focus styling must remain visible in the chosen theme.

## Security

Escaping and `SafeUrl` / `TrustedHtml` are framework concerns; authorization and data
exposure remain application code. Redact secrets before rendering.

## Common mistakes

- Never use LinkButton to submit a form or mutate data. Its `attrs=` seam remains validated and cannot override the owned destination or structural attributes.
- Do not copy docs-preview JavaScript into an application server.

## Testing

```python
from hedron import RenderMode, render

result = render(component, mode=RenderMode.FRAGMENT)
assert result.html
assert not result.diagnostics
```

[All component demos](index.md) · [Built-in API](../api/BUILT_INS.md) · [Testing](../guides/testing.md)

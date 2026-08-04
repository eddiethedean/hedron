---
title: Dialog
description: Present focused content in a native dialog with an explicit title and close path.
---

# `Dialog`

Present focused content in a native dialog with an explicit title and close path.

| | |
|---|---|
| Import | `from hedron import Dialog` |
| Distribution | `hedron` |
| Backend activity | No |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

<section class="hedron-component-demo" data-hedron-component-demo="Dialog"><div class="hdc-stage"><div class="hdc-dialog-launch"><span class="hdc-file-icon" aria-hidden="true">R</span><span><strong>Quarterly report</strong><small>Updated 2 minutes ago</small></span><button class="hdc-button" type="button" data-hdc-action="open-dialog">Delete…</button></div><dialog class="hdc-dialog" data-hdc-dialog aria-labelledby="hdc-dialog-title"><header><h2 id="hdc-dialog-title">Delete report?</h2><form method="dialog"><button type="submit" class="hdc-dialog-close" aria-label="Close dialog">×</button></form></header><p>This removes the saved report. The source data is unchanged.</p><footer><button class="hdc-button" type="button" data-hdc-action="close-dialog">Cancel</button><button class="hdc-button hdc-primary" type="button" data-hdc-action="close-dialog">Delete report</button></footer></dialog><p class="hdc-muted" role="status" data-hdc-status>Dialog closed.</p></div></section>

The preview is intentionally small enough to inspect with a keyboard and screen reader. It demonstrates the component's semantic result, not a screenshot. If the example represents HTMX activity, the “Simulated HTMX” trace confirms that documentation JavaScript supplied the response locally.

## Basic use

```python
from hedron import Dialog, Text

component = Dialog('Delete report', Text('This action cannot be undone.'), id='delete-report')
```

In a route, return the component inside a `Page`, or return it directly as a fragment through the framework adapter. Components are immutable descriptions of output: construct the complete state on the server and let the renderer serialize it.

## How it works

Dialog renders a native `<dialog>` with a level-two title, body region, built-in Close form using the browser's dialog submission method, and an optional actions slot. A button whose `data-hedron-dialog-open` value is the dialog's `#id` opens it through the shipped browser module; modal dialogs use `showModal()`, while `modal=False` uses `show()`. Already-open modal dialogs are upgraded to `showModal()` on boot and after HTMX swaps. The component never treats confirmation as authorization.

This component's core behavior is server-rendered HTML and does not require a browser runtime. The preview is ordinary semantic HTML, so keyboard, form, link, and disclosure behavior comes from the platform.

The component participates in Hedron's normal escaping, URL, and attribute validation. Values are data unless an API explicitly requires `SafeUrl` or reviewed `TrustedHtml`; do not pre-escape strings and do not concatenate HTML.

## Constructor and parameters

```python
Dialog(title, *nodes, children=None, open=False, modal=True, id=None, element_id=None)
```

| Parameter | Type | Meaning |
|---|---|---|
| `title` | `str` | Required dialog heading text. |
| `nodes` | `NodeLike` | Positional dialog body content. |
| `children` | `NodeLike | sequence | None` | Keyword body content; combines with positional nodes. |
| `open` | `bool` | Render the native open attribute initially. |
| `modal` | `bool` | Browser-module intent exposed as data-modal. |
| `id` | `str | None` | Stable ID for a trigger and focus restoration. |
| `element_id` | `str | None` | Compatibility alias for id. |

Keyword defaults are chosen for a safe, progressively enhanced baseline. Pass stable IDs when another component, a label, a URL fragment, a test, or an HTMX target must address the rendered node. Prefer typed component composition over hand-built HTML strings.

## Composition and backend behavior

Use `Dialog` at the smallest level that owns its semantics. Page routes normally compose it under `Page`, `Main`, and an explicit heading structure. HTMX fragment routes should return only the region being replaced and keep stable target IDs across success, validation, empty, loading, and error responses.

This component is primarily presentational; keep any mutation on an explicit action or component route.

## Accessibility

Open it from a clearly labelled trigger, place initial focus deliberately, support Escape and the Close control, and restore focus to the trigger when it closes.

Verify keyboard use, visible focus, zoom, and reduced motion for interactive states. Prefer native semantics and status/alert announcements over color-only cues.

## Security and validation

Escape and trust-boundary types (`SafeUrl`, `TrustedHtml`) remain framework concerns; authorization and data exposure remain yours. Redact secrets before rendering.

## Common mistakes

- The `open` attribute alone does not create modal focus trapping or background inertness; use the supported browser module to call `showModal()`.
- Do not copy docs-preview JavaScript into an application server; demos simulate HTMX locally.
- Choose components for semantics first, then theme them.

## Testing

```python
from hedron import RenderMode, render

result = render(component, mode=RenderMode.FRAGMENT)
assert result.html
assert not result.diagnostics
```

For interactive flows, assert method, URL, headers, fragment body, and status with a framework test client. Add a browser test when keyboard or HTMX swap behavior is material.

[All component demos](index.md) · [Built-in API baseline](../api/BUILT_INS.md) · [Testing UI](../guides/testing.md) · [Forms and actions](../guides/forms-and-actions.md)

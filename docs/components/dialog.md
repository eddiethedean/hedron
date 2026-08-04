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

Use `Dialog` at the smallest level that owns its semantics. Page routes normally compose it under `Page`, `Main`, and an explicit heading structure. HTMX routes should return only the component region being replaced and should preserve stable target IDs across success, validation, empty, loading, and error responses.

When a request can mutate data, use POST, validate CSRF, authenticate and authorize on the server, validate typed input again, and return a bounded fragment. GET interactions must remain safe and repeatable. Native links and forms should still reach a useful server response when HTMX is unavailable.

## Accessibility

Open it from a clearly labelled trigger, place initial focus deliberately, support Escape and the Close control, and restore focus to the trigger when it closes.

Test the demo and your application with keyboard-only input, visible focus, zoom, reduced motion, and at least one screen reader. Never make color, position, animation, or an icon the only carrier of state. Dynamic results need an appropriate status or alert and a deliberate focus strategy.

## Security and validation

Treat all request data, database content, filenames, URLs, labels, chart data, and Markdown as untrusted until the owning boundary validates it. Hedron escapes text and constrains dangerous surfaces, but it cannot decide application authorization or data exposure. Keep responses bounded, redact secrets before rendering, and use the narrowest URL and trust types available.

## Common mistakes

- The `open` attribute alone does not create modal focus trapping or background inertness; use the supported browser module to call `showModal()`.
- Do not copy the demo's JavaScript into a server application as a substitute for an HTMX endpoint. The simulation exists only because the hosted docs have no application backend.
- Do not select components by visual appearance alone; choose the native semantics first, then theme them.

## Testing

Render the component at the boundary you intend to ship and assert behavior rather than a large, brittle snapshot:

```python
from hedron import RenderMode, render

result = render(component, mode=RenderMode.FRAGMENT)
assert result.html
assert not result.diagnostics
```

For interactive use, add a framework test that sends the same method, URL, headers, and typed payload as the browser, then assert the returned fragment, status code, cache policy, and security headers. Add a browser test for keyboard behavior, focus, live announcements, and the HTMX swap lifecycle when those behaviors are material.

[All component demos](index.md) · [Built-in API baseline](../api/BUILT_INS.md) · [Testing UI](../guides/testing.md)

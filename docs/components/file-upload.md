---
title: FileUpload
description: Choose one or more local files with advisory browser constraints.
---

# `FileUpload`

Choose one or more local files with advisory browser constraints.

| | |
|---|---|
| Import | `from hedron import FileUpload` |
| Distribution | `hedron` |
| Backend activity | On enclosing form submit |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

<section class="hedron-component-demo" data-hedron-component-demo="FileUpload"><div class="hdc-stage"><label class="hdc-file"><span class="hdc-file-icon" aria-hidden="true">↑</span><strong>Upload evidence</strong><small>PDF, PNG, or JPG · up to 10 MB</small><input type="file" accept=".pdf,image/*" data-hdc-file></label><p class="hdc-muted" role="status" data-hdc-status>No file selected.</p></div></section>

The preview is intentionally small enough to inspect with a keyboard and screen reader. It demonstrates the component's semantic result, not a screenshot. If the example represents HTMX activity, the “Simulated HTMX” trace confirms that documentation JavaScript supplied the response locally.

## Basic use

```python
from hedron import FileUpload

component = FileUpload(name='evidence', accept='.pdf,image/*', maximum_size=10_000_000, label='Upload evidence')
```

In a route, return the component inside a `Page`, or return it directly as a fragment through the framework adapter. Components are immutable descriptions of output: construct the complete state on the server and let the renderer serialize it.

## How it works

The component renders a native file input and exposes the maximum size for progressive client feedback. The browser's accepted types and size hint are not security controls.

This component's core behavior is server-rendered HTML and does not require a browser runtime. The preview is ordinary semantic HTML, so keyboard, form, link, and disclosure behavior comes from the platform.

The component participates in Hedron's normal escaping, URL, and attribute validation. Values are data unless an API explicitly requires `SafeUrl` or reviewed `TrustedHtml`; do not pre-escape strings and do not concatenate HTML.

## Constructor and parameters

```python
FileUpload(*, name='file', accept=None, maximum_size=5_000_000, multiple=False, label='Upload file')
```

| Parameter | Type | Meaning |
|---|---|---|
| `name` | `str` | Multipart field name. |
| `accept` | `str | None` | Browser file-type hint. |
| `maximum_size` | `int` | Advisory size data attribute. |
| `multiple` | `bool` | Allow multiple selection. |
| `label` | `str` | Accessible and visible control label. |

Keyword defaults are chosen for a safe, progressively enhanced baseline. Pass stable IDs when another component, a label, a URL fragment, a test, or an HTMX target must address the rendered node. Prefer typed component composition over hand-built HTML strings.

## Composition and backend behavior

Use `FileUpload` at the smallest level that owns its semantics. Page routes normally compose it under `Page`, `Main`, and an explicit heading structure. HTMX fragment routes should return only the region being replaced and keep stable target IDs across success, validation, empty, loading, and error responses.

Mutating flows must use POST, validate CSRF, authorize on the server, re-validate typed input, and return a bounded fragment. GET remains safe and repeatable; native submit should still work without HTMX.

## Accessibility

Tell users accepted formats and limits before selection, and announce rejected files without clearing valid choices unnecessarily.

Verify keyboard use, visible focus, zoom, and reduced motion for interactive states. Prefer native semantics and status/alert announcements over color-only cues.

## Security and validation

Escape and trust-boundary types (`SafeUrl`, `TrustedHtml`) remain framework concerns; authorization and data exposure remain yours. Redact secrets before rendering.

## Common mistakes

- Validate filename, MIME/content, size, count, authorization, and storage location on the server.
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

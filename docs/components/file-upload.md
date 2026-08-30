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

The preview is a local docs simulation (not a running Hedron server). Interactive demos show a “Simulated HTMX” trace when applicable.

## Basic use

```python
from hedron import FileUpload
component = FileUpload(name='evidence', accept='.pdf,image/*', maximum_size=10_000_000, label='Upload evidence')
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

The component renders a native file input and exposes the maximum size for progressive client feedback. The browser's accepted types and size hint are not security controls.

This component's core behavior is server-rendered HTML and does not require a browser runtime. The preview is ordinary semantic HTML, so keyboard, form, link, and disclosure behavior comes from the platform.

## Constructor and parameters

```text
FileUpload(*, name='file', accept=None, maximum_size=5_000_000, multiple=False, label='Upload file')
```

| Parameter | Type | Meaning |
|---|---|---|
| `name` | `str` | Multipart field name. |
| `accept` | `str | None` | Browser file-type hint. |
| `maximum_size` | `int` | Advisory size data attribute. |
| `multiple` | `bool` | Allow multiple selection. |
| `label` | `str` | Accessible and visible control label. |

## Composition and backend behavior

Keep `FileUpload` at the smallest semantic boundary. Fragment routes should return only
the replaced region and preserve stable target IDs across success, validation, empty,
loading, and error responses.

Mutating flows must use POST, validate CSRF, authorize on the server, re-validate typed input, and return a bounded fragment. GET remains safe and repeatable; native submit should still work without HTMX.

## Accessibility

Tell users accepted formats and limits before selection, and announce rejected files without clearing valid choices unnecessarily.

## Security

Escaping and `SafeUrl` / `TrustedHtml` are framework concerns; authorization and data
exposure remain application code. Redact secrets before rendering.

## Common mistakes

- Validate filename, MIME/content, size, count, authorization, and storage location on the server.
- Do not copy docs-preview JavaScript into an application server.

## Testing

```python
from hedron import RenderMode, render

result = render(component, mode=RenderMode.FRAGMENT)
assert result.html
assert not result.diagnostics
```

[All component demos](index.md) · [Built-in API](../api/BUILT_INS.md) · [Testing](../guides/testing.md)

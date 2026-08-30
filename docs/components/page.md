---
title: Page
description: Render a complete HTML document with safe head defaults and a body.
---

# `Page`

Render a complete HTML document with safe head defaults and a body.

| | |
|---|---|
| Import | `from hedron import Page` |
| Distribution | `hedron` |
| Backend activity | Page response |
| Normal render mode | `RenderMode.PAGE` |

## Live demo

<section class="hedron-component-demo" data-hedron-component-demo="Page"><div class="hdc-stage"><div class="hdc-browser"><div><i></i><i></i><i></i><span data-hdc-title>Account · Acme</span></div><main><h3>Account</h3><p>Signed in as ada@example.com</p></main></div></div></section>

The preview is a local docs simulation (not a running Hedron server). Interactive demos show a “Simulated HTMX” trace when applicable.

## Basic use

```python
from hedron import Header, Heading, Main, Page, Text
component = Page(Header(Heading('Account', level=1)), Main(Text('Signed in')), title='Account', htmx_extensions=())
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

`Page` owns the outer `html`, `head`, and `body` elements. It always emits UTF-8 and responsive viewport metadata, then adds the title and optional head slot before rendering body children. Optional `scripts=` emits allowlisted same-origin script tags after body children.

This component's core behavior is server-rendered HTML and does not require a browser runtime. The preview is ordinary semantic HTML, so keyboard, form, link, and disclosure behavior comes from the platform.

## Constructor and parameters

```text
Page(*body, lang='en', title=None, head=None, children=None, data_theme=None, data_hedron_theme=None, dir=None, scripts=None, script_defer=True)
```

| Parameter | Type | Meaning |
|---|---|---|
| `body / children` | `NodeLike` | Body nodes; use either positional children or `children=`. |
| `lang` | `str` | The document language written to `<html lang>`. |
| `title` | `str | None` | Convenience document title. |
| `head` | `NodeLike | None` | Additional trusted head nodes. |
| `data_theme` | `str | None` | Initial `data-theme` value. |
| `data_hedron_theme` | `str | None` | Named Hedron theme for this document; overrides the app selection. |
| `dir` | `str | None` | Optional `dir` on `<html>` (`ltr` / `rtl` / `auto`). |
| `scripts` | `Sequence[SafeUrl] | None` | Allowlisted same-origin `SafeUrl` ASSET scripts; free-form `<script>` nodes stay out of the tree. |
| `script_defer` | `bool` | When true (default), emitted script tags use `defer`. |

## Composition and backend behavior

Keep `Page` at the smallest semantic boundary. Fragment routes should return only
the replaced region and preserve stable target IDs across success, validation, empty,
loading, and error responses.

`Page` is primarily presentational; keep any mutation on an explicit action or component route.

## Accessibility

Set `lang` to the language of the page and keep exactly one main landmark in the body. Pass only `SafeUrl` ASSET paths in `scripts=` (root-relative, same-origin).

## Security

Escaping and `SafeUrl` / `TrustedHtml` are framework concerns; authorization and data
exposure remain application code. Redact secrets before rendering.

## Common mistakes

- Do not return `Page` for an HTMX fragment request; use `Fragment` and fragment render mode instead.
- Do not copy docs-preview JavaScript into an application server.

## Testing

```python
from hedron import RenderMode, render

result = render(component, mode=RenderMode.PAGE)
assert result.html
assert not result.diagnostics
```

[All component demos](index.md) · [Built-in API](../api/BUILT_INS.md) · [Testing](../guides/testing.md)

---
title: MasterDetail
description: Responsive master-detail layout with named fragment regions.
---

# `MasterDetail`

Responsive master-detail layout with named fragment regions.

| | |
|---|---|
| Import | `from hedron import MasterDetail` |
| Distribution | `hedron` |
| Backend activity | No |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

<section class="hedron-component-demo" data-hedron-component-demo="MasterDetail"><div class="hdc-stage"><div class="hdc-grid"><nav aria-label="Master list"><small>Items</small><strong>Alpha</strong><em>Selected</em></nav><section aria-label="Detail panel"><small>Detail</small><strong>Alpha</strong><em>Ready</em></section></div></div></section>

The preview is a local docs simulation (not a running Hedron server). Interactive demos show a “Simulated HTMX” trace when applicable.

## Basic use

```python
from hedron import MasterDetail, Text

component = MasterDetail(Text('Items'), Text('Detail'), master_id='master', detail_id='detail')
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

MasterDetail composes list/detail workspaces with theme-owned ratios and region ids for fragment updates.

This component's core behavior is server-rendered HTML and does not require a browser runtime. The preview is ordinary semantic HTML, so keyboard, form, link, and disclosure behavior comes from the platform.

## Constructor and parameters

```python
MasterDetail(master, detail=None, *, ratio='1:2', collapse='md', master_id='master', detail_id='detail', state='ready', empty_message='Select an item')
```

| Parameter | Type | Meaning |
|---|---|---|
| `master / detail` | `NodeLike` | List pane and detail pane content. |
| `state` | `str` | `ready` / `loading` / `empty` / `error` / `permission`. |
| `master_id / detail_id` | `str` | Named fragment region ids for HTMX swaps. |
| `ratio` | `str` | Closed split ratio such as `1:2` or `1:1`. |
| `collapse` | `str` | Breakpoint where panes stack (`never` / `sm` / `md` / `lg`). |

## Composition and backend behavior

Keep `MasterDetail` at the smallest semantic boundary. Fragment routes should return only
the replaced region and preserve stable target IDs across success, validation, empty,
loading, and error responses.

`MasterDetail` is primarily presentational; keep any mutation on an explicit action or component route.

## Accessibility

Use permission/empty/error states so denied or missing selections never leak detail content.

## Security

Escaping and `SafeUrl` / `TrustedHtml` are framework concerns; authorization and data
exposure remain application code. Redact secrets before rendering.

## Common mistakes

- Do not invent CSS escapes for pane sizing; stay on the closed ratio vocabulary.
- Do not copy docs-preview JavaScript into an application server.

## Testing

```python
from hedron import RenderMode, render

result = render(component, mode=RenderMode.FRAGMENT)
assert result.html
assert not result.diagnostics
```

[All component demos](index.md) · [Built-in API](../api/BUILT_INS.md) · [Testing](../guides/testing.md)

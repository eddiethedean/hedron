---
title: ConnectorNode
description: Provider-neutral source or destination node for data-movement workflows.
---

# `ConnectorNode`

Provider-neutral source or destination node for data-movement workflows.

| | |
|---|---|
| Import | `from hedron import ConnectorNode` |
| Distribution | `hedron` |
| Backend activity | No |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

<section class="hedron-component-demo" data-hedron-component-demo="ConnectorNode"><div class="hdc-stage"><article class="hdc-connector-node"><div class="hdc-inline"><span class="hdc-badge">CSV</span><strong>Source</strong></div><small>Ready · Local upload</small><em>orders.csv</em></article></div></section>

The preview is a local docs simulation (not a running Hedron server). Interactive demos show a “Simulated HTMX” trace when applicable.

## Basic use

```python
from hedron import ConnectorNode

component = ConnectorNode('Warehouse', kind='target', state='ready', detail='Destination', runtime='Postgres')
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

ConnectorNode owns provider-neutral semantic markers and the baseline responsive node treatment. Applications supply provider identity and metadata as content, so workflow styling does not depend on private application selectors.

This component's core behavior is server-rendered HTML and does not require a browser runtime. The preview is ordinary semantic HTML, so keyboard, form, link, and disclosure behavior comes from the platform.

## Constructor and parameters

```python
ConnectorNode(label, *nodes, children=None, kind='source', state='ready', detail=None, runtime=None, leading=None, id=None, class_=None)
```

| Parameter | Type | Meaning |
|---|---|---|
| `label` | `str` | Discernible source or destination name. |
| `nodes / children` | `NodeLike` | Optional metadata content rendered inside the node. |
| `kind` | `source | target` | Connector role in the workflow. |
| `state` | `ready | blocked | running | succeeded | failed` | Explicit operational state. |
| `detail / runtime` | `str | None` | Supporting context such as object or runtime. |
| `leading` | `NodeLike | None` | Optional provider mark or identity content. |

## Composition and backend behavior

Keep `ConnectorNode` at the smallest semantic boundary. Fragment routes should return only
the replaced region and preserve stable target IDs across success, validation, empty,
loading, and error responses.

`ConnectorNode` is primarily presentational; keep any mutation on an explicit action or component route.

## Accessibility

Keep the label and state text visible; state is never communicated by color alone.

## Security

Escaping and `SafeUrl` / `TrustedHtml` are framework concerns; authorization and data
exposure remain application code. Redact secrets before rendering.

## Common mistakes

- Do not encode a provider name into the component type or replace the state text with an icon-only indicator.
- Do not copy docs-preview JavaScript into an application server.

## Testing

```python
from hedron import RenderMode, render

result = render(component, mode=RenderMode.FRAGMENT)
assert result.html
assert not result.diagnostics
```

[All component demos](index.md) · [Built-in API](../api/BUILT_INS.md) · [Testing](../guides/testing.md)

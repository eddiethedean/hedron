---
title: AsyncRegion
description: Server-authored lifecycle boundary with ordinary HTML fallbacks.
---

# `AsyncRegion`

Render one stable region for initial, pending, empty, success, error, timeout, cancelled,
retry, and conflict states.

| | |
|---|---|
| Import | `from hedron import AsyncRegion` |
| Distribution | `hedron-core` / `hedron` |
| Backend activity | No; the route or action remains server-owned |
| Normal render mode | `RenderMode.FRAGMENT` |

## Basic use

```python
from hedron import AsyncRegion, Button, Text

component = AsyncRegion(
    Text("Report ready"),
    state="success",
    pending=Text("Loading report…"),
    error=Text("The report could not be loaded."),
    retry=Button("Try again"),
    fallback="fragment",
    label="Report",
)
```

`AsyncRegion` selects one named slot on the server and emits a stable `div` with
`data-hedron-action-phase`, `aria-busy`, and a declared fallback marker. The fallback is
ordinary HTML or a full fragment/page response; no hydration or browser store is required.

## Constructor and parameters

```python
AsyncRegion(*nodes, state='idle', initial=None, pending=None, empty=None,
            success=None, error=None, timeout=None, cancelled=None,
            retry=None, conflict=None, fallback='fragment', label=None)
```

`state` accepts the lifecycle vocabulary plus `empty` and `timeout`. Passing `fallback='page'`
records that a full-page response is the safe enhancement-free boundary. A slot is optional;
when it is absent, the normal children remain available as the fallback content.

## Accessibility and security

The region is labelled only when `label` is provided. Pending state sets `aria-busy="true"`;
the status text itself remains application content, so it should explain what changed without
exposing secrets. Cancellation and stale results are presentation outcomes, not authorization
decisions.

## Testing

```python
from hedron import render

assert 'data-hedron-action-phase="pending"' in render(
    AsyncRegion("result", state="pending", pending="Loading")
).html
```

[All component demos](index.md) · [Interaction API](../api/INTERACTION.md)

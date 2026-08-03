---
status: shipped
---

# Interaction APIs

**Status:** Shipped in `0.6.0`

Typed FastAPI/HTMX request and result contracts live in `hedron.interaction` and are
re-exported from `hedron`.

## `HtmxRequest`

Wrap a Starlette/FastAPI request with HTMX context:

```python
from fastapi import Request
from hedron import htmx_request

def handler(request: Request):
    hx = htmx_request(request)
    if hx.is_htmx:
        _ = hx.target, hx.boosted, hx.history_restore
```

## `InteractionPolicy` and fragment regions

```python
from hedron import FragmentRegion, InteractionPolicy, InteractionResult, Text

policy = InteractionPolicy(
    hx_sync="drop",
    indicator="#busy",
    aria_busy=True,
    vary_on_target=True,
    declared_regions=(
        FragmentRegion(id="main", selector="#main", description="Primary panel"),
    ),
)

result = InteractionResult(
    content=Text("Updated"),
    region_id="main",
    policy=policy,
)
```

Unauthorized `HX-Target` values against `declared_regions` raise at resolve time
(`resolve_fragment_region`). Declare regions on routes via router/`fragment_regions`
when you need an allowlist of swap targets.

## `status_policy_for`

```python
from hedron.interaction import status_policy_for

policy = status_policy_for(422)
# StatusPolicy(status_code=422, message="Validation failed", reswap="innerHTML", ...)
```

Built-in defaults cover 202, 204, 401, 403, 409, 422, 429, and 500.

## `form_sync_attrs`

Emit HTMX/accessibility attributes for synchronized forms and search:

```python
from hedron import form_sync_attrs, default_interaction_policy

attrs = form_sync_attrs(default_interaction_policy(indicator="#spinner"))
# {"hx-sync": "drop", "hx-indicator": "#spinner", "aria-busy": "true"}
```

## Cache `Vary`

Prefer `InteractionResult(cache="vary-htmx")` so page vs fragment vs history-restore
responses do not confuse shared caches. Enable `vary_on_target=True` when the same URL
serves multiple authorized fragment regions.

Full response shape: [Responses](RESPONSES.md). Walkthrough: [Charts and HTMX](../guides/charts-and-htmx.md).

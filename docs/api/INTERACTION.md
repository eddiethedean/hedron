---
status: shipped
---

# Interaction APIs


!!! note "Stability (0.8 compatibility baseline)"

    Classifications for this surface are recorded in [STABILITY.md](STABILITY.md). Package maturity (Beta/Alpha) is separate from API level (`beta` / `experimental` / `internal` / `deferred`).

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

Prefer declaring the allowlist on the route:

```python
from hedron import FragmentRegion, InteractionResult, Text

MAIN = FragmentRegion(id="main", selector="#main", description="Primary panel")


@app.component("/panel", fragment_regions=(MAIN,))
def panel() -> InteractionResult:
    return InteractionResult(content=Text("Updated"), region_id=MAIN.id)
```

Route-declared regions are authoritative and are merged into the result policy. An HTMX
request with an `HX-Target` outside that allowlist receives `403`. `page` and `component`
routes accept `fragment_regions`; values may be `FragmentRegion` instances or IDs, which
are normalized to `#id` selectors.

For lower-level use, `resolve_fragment_region(policy, target)` returns the matching region
or raises `FragmentRegionError` when the target is unauthorized.

## `InteractionResult`

`InteractionResult` keeps fragment mechanics typed and inspectable:

| Area | Fields | Notes |
|---|---|---|
| Content | `content`, `status_code`, `region_id` | Primary body, HTTP status, and declared destination. |
| Swap | `target`, `swap`, `retarget`, `reswap`, `reselect` | Selectors are checked against Hedron's safe subset. |
| Events | `trigger`, `trigger_after_swap`, `trigger_after_settle` | Strings or mappings encoded as `HX-Trigger*`. |
| Navigation | `redirect`, `location`, `push_url`, `replace_url`, `history` | URL-bearing headers require local paths. |
| Cache | `cache` | `private`, `no-store`, `vary-htmx`, or `None`. |
| Additional updates | `oob` | A tuple of `OobUpdate` values. |
| Diagnostics | `explanation` | Visible to Explorer traces; it is not rendered. |

Prefer these fields over `headers`. If `headers` is needed, Hedron accepts only approved
`HX-*`, `Cache-Control`, and `Vary` names and re-validates URL and selector values.

### Out-of-band updates

```python
from hedron import InteractionResult, OobUpdate, Text

result = InteractionResult(
    content=Text("Primary update"),
    oob=(
        OobUpdate(
            content=Text("Saved"),
            element_id="status",
            swap="true",
        ),
    ),
)
```

`element_id` asks Hedron to wrap the content with the corresponding `hx-swap-oob`
element. When the route declares fragment regions, OOB `element_id` and `select` values
must also resolve to authorized regions. With declared regions, materialization **binds**
the rendered OOB target to the authorized `#id` (select-only `#id` is rewritten to that
id); `element_id` must match an authorized `select="#…"` when both are set. Callers cannot
use `select="#main"` to authorize content that swaps a different id.

`Cache-Control: public` / `s-maxage` in `headers` extras is rejected. Typed `cache=`
policy owns private/no-store behavior.

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

| Hint | Response behavior |
|---|---|
| `vary-htmx` | Adds `Vary: HX-Request, HX-History-Restore-Request`; also `HX-Target` with `vary_on_target=True`. |
| `private` | Adds `Cache-Control: private`. |
| `no-store` | Adds `Cache-Control: private, no-store`. |
| `None` | Adds no interaction-specific cache header. |

Prefer `vary-htmx` when one URL can return both a document and a fragment. Enable
`vary_on_target=True` when it serves multiple authorized fragment regions. Use
`no-store` for sensitive or user-specific results that must not be retained.

Full response shape: [Responses](RESPONSES.md). Walkthrough:
[Build an HTMX interaction](../guides/htmx-interactions.md).

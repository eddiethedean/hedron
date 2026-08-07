---
status: shipped
---

# Interaction APIs


!!! note "Stability"

    Classifications for this surface are recorded in [STABILITY.md](STABILITY.md). Package maturity (Beta/Alpha) is separate from API level (`beta` / `experimental` / `internal` / `deferred`).

**Status:** Shipped (fragment regions + `InteractionResult` on the **0.19** Ready-to-cut train; last published `v0.18.0`)

Typed FastAPI/HTMX request and result contracts live in `hedron.interaction` and are
re-exported from `hedron`.

HDJ templates may use HTMX's native `hx-*` and `hx-on:*` attributes directly. These Python APIs
remain the preferred server-side boundary for response headers, declared regions, OOB updates,
cache policy, and diagnostics; they are not a reduced client-side HTMX dialect. See
[HDJ authoring](JINJA.md#htmx).

## Errors

| Situation | Result | What to do |
|---|---|---|
| HTMX request with `HX-Target` but no route `fragment_regions` | HTTP **403** | Declare `FragmentRegion`s on `@app.component` / `@app.page`, or opt out only with `InteractionPolicy(allow_undeclared_targets=True)` |
| `HX-Target` / `region_id` outside the declared allowlist | HTTP **403** / `FragmentRegionError` | Match `region_id` and HTMX target to a declared `FragmentRegion.id` / selector |
| Unsafe selector or external redirect in typed fields | Rejected before emit | Use local paths and Hedron's safe selector subset |
| Unauthorized OOB `select` / `element_id` when regions are declared | Rejected | Point OOB updates at authorized region ids |
| `Cache-Control: public` (or `s-maxage`) via `headers` | Rejected | Use typed `cache=` (`private` / `no-store` / `vary-htmx`) |
| CSRF failure on POST (host profile) | HTTP **403** | Seed CSRF on GET; include token on POST — [Troubleshooting](../guides/troubleshooting.md#csrf-403-on-post-fastapi-flask) |

See also [HTMX interactions](../guides/htmx-interactions.md) and [Error codes](../guides/error-codes.md).

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

Route-declared regions are authoritative and are merged into the result policy. HTMX
requests that send `HX-Target` **require** declared regions by default (fail closed);
undeclared targets or an empty allowlist receive `403`. Opt out only with
`InteractionPolicy(allow_undeclared_targets=True)`. `page` and `component` routes accept
`fragment_regions`; values may be `FragmentRegion` instances or IDs, which are normalized
to `#id` selectors.

For lower-level use, `authorize_htmx_target(policy, target, is_htmx=...)` / 
`resolve_fragment_region(policy, target)` raise `FragmentRegionError` when unauthorized.

## Day-1 ergonomics (`swap`, `retarget`, `redirect_htmx`, `RefreshButton`)

These helpers are re-exported from `hedron` and are what the Quickstart / HTMX guides use.
They return `InteractionResult` (except `RefreshButton`, which is a component).

### `swap(content, *, toast=None, oob=(), **kwargs) -> InteractionResult`

Primary fragment body with optional toast / OOB updates. Extra kwargs pass through to
`InteractionResult` (`region_id`, `trigger`, `cache`, …).

```python
from hedron import swap

@app.fragment("/status", region=status)
def refresh_status():
    return swap(status_panel())
```

| Parameter | Type | Meaning |
|---|---|---|
| `content` | `NodeLike \| None` | Primary swap body |
| `toast` | `str \| NodeLike \| OobUpdate \| None` | Convenience OOB toast (`#hedron-toast`) |
| `oob` | sequence of `OobUpdate \| NodeLike` | Additional out-of-band updates |
| `**kwargs` | | Forwarded to `InteractionResult` |

Related: `swap_oob(content, *oob, **kwargs)` — primary fragment plus one or more OOB
updates as positional args.

### `retarget(content, region, **kwargs) -> InteractionResult`

Return content with an approved `HX-Retarget` selector. Pass a `FragmentRegion` or a
selector string. When given a region, sets `region_id` if not already provided.

```python
from hedron import retarget

return retarget(Text("Moved"), status)
```

### `redirect_htmx(url: str) -> InteractionResult`

Issue an HTMX `HX-Redirect` for a **local** path (validated like other URL-bearing fields).

```python
from hedron import redirect_htmx

return redirect_htmx("/login")
```

### `RefreshButton.for_region(region, *, href, label=...)`

Component that issues a GET to `href` targeting the declared region (HTMX swap into
`#region.id`). Pair with `@app.fragment(path, region=...)` returning `swap(...)`.

```python
from hedron import RefreshButton

status = app.region("service-status", description="Live status panel")
RefreshButton.for_region(status, href="/status", label="Refresh status")
```

| Situation | Result |
|---|---|
| Fragment `HX-Target` not on the route allowlist | HTTP **403** |
| Redirect URL is not local | Rejected before emit |

Walkthrough: [HTMX interactions](../guides/htmx-interactions.md).

## `InteractionResult`

`InteractionResult` keeps fragment mechanics typed and inspectable.

### Constructor fields

| Field | Type (conceptual) | Meaning |
|---|---|---|
| `content` | `NodeLike \| None` | Primary fragment body |
| `status_code` | `int` | HTTP status (default 200) |
| `region_id` | `str \| None` | Declared destination region id |
| `target` / `swap` / `retarget` / `reswap` / `reselect` | `str \| None` | Swap controls; selectors use Hedron's safe subset |
| `trigger` / `trigger_after_swap` / `trigger_after_settle` | `str \| Mapping \| None` | Encoded as `HX-Trigger*` |
| `redirect` / `location` / `push_url` / `replace_url` / `history` | local URL fields | URL-bearing headers require local paths |
| `cache` | `private` \| `no-store` \| `vary-htmx` \| `None` | Cache / Vary policy |
| `oob` | `tuple[OobUpdate, ...]` | Out-of-band updates |
| `policy` | `InteractionPolicy \| None` | Sync/indicator/region defaults |
| `explanation` | `str \| None` | Explorer/diagnostics only; not rendered |
| `headers` | escape hatch | Approved `HX-*`, `Cache-Control`, `Vary` only |

### Return / response behavior

Handlers may return `InteractionResult`, a component/`NodeLike`, or (on some routes)
ordinary FastAPI responses. When Hedron renders an `InteractionResult` as an HTMX
fragment it emits HTML for `content`, applies validated `HX-*` headers, and enforces
route `fragment_regions` (unauthorized `HX-Target` → `403`).

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

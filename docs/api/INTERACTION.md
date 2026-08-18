---
status: shipped
---

# Interaction APIs


!!! note "Stability"

    Classifications for this surface are recorded in [STABILITY.md](STABILITY.md). Package maturity (Beta/Alpha) is separate from API level (`beta` / `experimental` / `internal` / `deferred`).

**Status:** Shipped (fragment regions + `InteractionResult`; living train **0.50.x**)

Day-to-day apps should start with [`@app.refreshable` / `@app.command`](../getting-started/interaction-apis.md).
This page documents the explicit region / `InteractionResult` contracts those handles compile to.

Typed FastAPI/HTMX request and result contracts live in `hedron.interaction` and are
re-exported from `hedron`.

HDJ templates may use HTMX's native `hx-*` and `hx-on:*` attributes directly. These Python APIs
remain the preferred server-side boundary for response headers, declared regions, OOB updates,
cache policy, and diagnostics; they are not a reduced client-side HTMX dialect. See
[HDJ authoring](JINJA.md#htmx).

## Parameters (core types)

| Symbol | Key inputs | Role |
|---|---|---|
| `FragmentRegion` | `id`, `selector`, `description` | Declared HTMX target allowlist entry |
| `InteractionPolicy` | `declared_regions`, `allow_undeclared_targets`, `hx_sync`, `vary_on_target`, `embed_csrf`, `indicator`, … | Route/fragment authorization + sync policy |
| `InteractionResult` | `content`, `region_id`, `oob`, `status_code`, `cache`, `refresh`, `concurrency`, HTMX overrides | Typed fragment response + headers |
| `htmx_request(request)` | Starlette/FastAPI `Request` | Read HTMX request context |
| `swap` / `retarget` / `redirect_htmx` | content / target / local URL | Day-1 ergonomics over `InteractionResult` |

Field-level detail for `InteractionResult` is below. Autodoc signatures: [AUTODOC.md](AUTODOC.md).

## Errors

| Situation | Result | What to do |
|---|---|---|
| HTMX request with `HX-Target` but no route `fragment_regions` | HTTP **403** | Declare `FragmentRegion`s on `@app.component` / `@app.page`, or opt out only with `InteractionPolicy(allow_undeclared_targets=True)` |
| HTMX request with declared regions but missing `HX-Target` | HTTP **403** / `FragmentRegionError` | Send a matching `HX-Target` (no implicit first-region authorization). Exception: `HX-History-Restore-Request` may omit `HX-Target` (full-page restore). |
| `HX-Target` / `region_id` outside the declared allowlist | HTTP **403** / `FragmentRegionError` | Match `region_id` and HTMX target to a declared `FragmentRegion.id` / selector |
| Unsafe selector or external redirect in typed fields | Rejected before emit | Use local paths and Hedron's safe selector subset |
| Unauthorized OOB `select` / `element_id` | Rejected | Point OOB at declared region ids, or use reserved `hedron-toast` |
| OOB updates on HTTP **204** | HTTP **403** (all hosts) | Do not combine `status_code=204` with `oob=` |
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

### `InteractionPolicy` fields

| Field | Type | Default | Meaning |
|---|---|---|---|
| `hx_sync` | `str \| None` | `"drop"` | HTMX sync strategy hint for competing requests |
| `indicator` | `str \| None` | `None` | Selector for a busy indicator |
| `aria_busy` | `bool` | `True` | Whether to advertise busy state |
| `embed_csrf` | `bool` | `True` | Prefer embedding CSRF tokens in forms/responses when the host profile requires them |
| `restore_focus` | `bool` | `True` | Prefer restoring focus after swap when supported |
| `idempotent_get` | `bool` | `True` | Treat GET fragment refreshes as safe/repeatable |
| `error_retarget` | `str \| None` | `None` | Optional retarget selector for error responses |
| `error_reswap` | `str \| None` | `"innerHTML"` | Reswap strategy for error responses |
| `vary_on_target` | `bool` | `False` | Include target in cache Vary behavior when enabled |
| `declared_regions` | `tuple[FragmentRegion, ...]` | `()` | Allowlisted HTMX targets for this result/route |
| `allow_undeclared_targets` | `bool` | `False` | Opt out of fail-closed target authorization (avoid in production) |
| `history_restore` | `"page"` / `"primary"` / `"oob"` | `"page"` | How history restore should rebuild the document. Keep HTMX `historyRestoreAsHxRequest:false`; do not add app `htmx:historyRestore` handlers. |

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

## Returns

| Symbol | Returns |
|---|---|
| `FragmentRegion(...)` | Frozen region descriptor (`id`, `selector`, `description`) |
| `InteractionPolicy(...)` | Frozen HTMX/cache/aria policy for a result |
| `InteractionResult(...)` | Typed fragment result consumed by `HedronRoute` / adapters |
| `htmx_request(request)` | `HtmxRequest` view over HTMX headers |
| `swap` / `swap_oob` / `retarget` / `redirect_htmx` | `InteractionResult` (or redirect response for `redirect_htmx`) |
| `authorize_htmx_target` / `resolve_fragment_region` | Authorization / region lookup; raises `FragmentRegionError` when denied |

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
| `HX-Retarget` / `HX-Reselect` not on the route allowlist (and not a reserved sink) | Rejected before emit / HTTP **403** |
| `HX-Location` JSON `target` / `select` not on the route allowlist | Rejected before emit / HTTP **403** |
| Redirect URL is not local | Rejected before emit |

Reserved response sinks that do not need a route declaration: `#hedron-toast`,
`#hedron-errors`, `#hedron-auth`. Set `InteractionPolicy.allow_undeclared_targets=True`
to opt out of region membership checks for inbound and outbound selectors.

Walkthrough: [HTMX interactions](../guides/htmx-interactions.md).

## `InteractionResult`

`InteractionResult` keeps fragment mechanics typed and inspectable.

### Constructor fields

| Field | Type (conceptual) | Default | Meaning |
|---|---|---|---|
| `content` | `NodeLike \| None` | `None` | Primary fragment body |
| `status_code` | `int` | `200` | HTTP status |
| `region_id` | `str \| None` | `None` | Declared destination region id |
| `target` / `swap` / `retarget` / `reswap` / `reselect` | `str \| None` | `None` | Swap controls; selectors use Hedron's safe subset |
| `trigger` / `trigger_after_swap` / `trigger_after_settle` | `str \| Mapping \| None` | `None` | Encoded as `HX-Trigger*` |
| `redirect` / `location` / `push_url` / `replace_url` / `history` | local URL fields | `None` / `"none"` | URL-bearing headers require local paths; `history` defaults to `"none"` |
| `refresh` | `bool` | `False` | When `True`, emit `HX-Refresh` |
| `cache` | `private` \| `no-store` \| `vary-htmx` \| `None` | `"vary-htmx"` | Cache / Vary policy |
| `concurrency` | `str \| None` | `None` | Optional concurrency token / key for adaptive controls |
| `oob` | `tuple[OobUpdate, ...]` | `()` | Out-of-band updates |
| `policy` | `InteractionPolicy \| None` | `None` | Sync/indicator/region defaults |
| `explanation` | `str` | `""` | Explorer/diagnostics only; not rendered |
| `headers` | mapping escape hatch | `{}` | Approved `HX-*`, `Cache-Control`, `Vary` only |

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
| Navigation | `redirect`, `location`, `push_url`, `replace_url`, `history`, `refresh` | URL-bearing headers require local paths; `refresh=True` emits `HX-Refresh`. |
| Cache / concurrency | `cache`, `concurrency` | `cache` defaults to `vary-htmx`; `concurrency` is optional. |
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

#### `hx-select-oob` vs `OobUpdate` (one mechanism per target)

Request-side `HtmxLink(..., select_oob="#side-nav")` asks HTMX to **select** matching
nodes from the response for OOB handling. Server-side `OobUpdate(element_id="side-nav",
swap="innerHTML")` already emits a Hedron `hx-swap-oob` envelope. Combining both for the
same id can replace a semantic shell host (for example
`<nav id="side-nav" aria-label="Account navigation">`) with Hedron's wrapper
(`<div id="side-nav" hx-swap-oob="innerHTML">`), dropping the landmark tag and accessible
name.

Recommended shell pattern: return explicit `OobUpdate` and **omit** matching `select_oob`.
Use `conflicting_select_oob_targets(...)` or `hedron check` (`HED-HTMX-0002`) when both
appear with literal metadata in the same file.

Optional `OobUpdate(tag="nav")` (allowlisted: `div`, `section`, `aside`, `main`, `nav`) is
**defense in depth** if an envelope must match a landmark host—it is not a substitute for
avoiding the conflict.

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
| `vary-htmx` | Emits `Cache-Control: private, no-store` plus `Vary: HX-Request, HX-History-Restore-Request`; also `HX-Target` when `vary_on_target=True` or more than one declared region. |
| `private` | Adds `Cache-Control: private`. |
| `no-store` | Adds `Cache-Control: private, no-store`. |
| `None` | Adds no interaction-specific cache header. |

Prefer `vary-htmx` when one URL can return both a document and a fragment. Enable
`vary_on_target=True` when it serves multiple authorized fragment regions. Use
`no-store` for sensitive or user-specific results that must not be retained.

Full response shape: [Responses](RESPONSES.md). Walkthrough:
[Build an HTMX interaction](../guides/htmx-interactions.md).

## 0.50 authoring primitives

These compile into existing `Hx` / `ActionHandle` / reserved OOB. They are not Explorer APIs
and do not use `fetch()`, `hx-on*`, `js:` vals, or extra HTMX extensions.

### `Hx`

`trigger`, `include`, `validate="native"` (`hx-validate="true"` plus optional
`data-hedron-validity="native"`), and `vals` / `headers` without `js:` expressions.
CSRF stays framework-injected (`X-CSRF-Token` + cookie `hedron_csrf`). Native HTML
`reportValidityOfForms` remains true; HTTP 422 stays authoritative.

### `ActionHandle.effect` / `.after`

`handle.effect(refresh(status).toast("Saved"))` keeps the CSRF POST and defaults
`hx-swap="none"` when success is refresh+toast / `InteractionResult`.
`handle.after(load=..., when=..., delay_ms=...)` compiles to `hx-trigger` delay/filter
or `data-hedron-after-load` for `HX-Trigger-After-Swap` — not `setTimeout` / `click()`.
`effect()` / `after()` return copies (`dataclasses.replace`); command success applies
the registered effect as OOB refresh+toast / `InteractionResult`.

### Dependent `Select` / `Control(depends_on=)`

Child `hx-get` fragment + `hx-trigger="change from:#…"` + `hx-include`. The server
synthesizes options at `Control.source`.

### `Lazy` / `FragmentHost(error=ErrorState(...))`

Authors do not write `hx-on`. Both `hedron-ui.mjs` copies (`hedron-core` static and
`hedron/static`, kept byte-identical) listen for `htmx:responseError` /
`htmx:sendError` and swap the `data-hedron-error-template` kept outside the inner
`#…-body` Lazy swap target.

### `Toast(..., ttl_ms=)` / `ToastHost()`

Frozen `#hedron-toast` OOB sink. Queue, TTL, and danger dismiss live in both
`hedron-ui.mjs` copies. Danger toasts
keep no TTL unless an author sets one.


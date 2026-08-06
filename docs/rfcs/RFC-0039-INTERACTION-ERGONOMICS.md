# RFC-0039: Interaction authoring ergonomics

**Status:** Implemented
**Phase:** 0.15 (`v0.15.0`) — additive DX over existing HTMX contracts
**Roadmap:** named in phase 0.15 entry gate, scope, exit gate, capability inventory, and
**Related:** RFC-0007 (Explorer), RFC-0008 (addressable), RFC-0009 (HTMX), RFC-0015 (routing),

## Summary

Reduce ceremony for the common HTMX loop (declare region → wire control → return fragment) with
three additive ergonomics:

1. **`region` + `@fragment` one-liner API** — one object/decorator owns id, selector, and route
   registration.
2. **`swap(...)` builders** — human recipes over `InteractionResult` without hiding the envelope.
3. **Dev-mode region diagnostics + Explorer “what will this click do?”** — fail-closed stays; mistakes
   become teachable.

Production authorization, PAGE vs FRAGMENT modes, and “rendering ≠ exposure” are unchanged.

## Motivation and background

The HTMX guide’s first interaction still requires a `FragmentRegion`, matching DOM id/selector,
component route `fragment_regions=`, and often an explicit `InteractionResult`. That is correct and
inspectable — and heavier than Streamlit/NiceGUI migrants expect for “refresh this panel.”

Fail-closed undeclared `HX-Target` (403) is a feature; first-hour errors currently read as opaque
HTTP failures rather than “typo in region id.”

## Proposed design

### 1. `region` and `@fragment`

```python
status = app.region("service-status", description="Live status panel")

@app.fragment("/status", region=status)  # or regions=[status]
def status_fragment():
    return status_panel()  # content only; mode/region auth from decorator + HX headers

@app.page("/")
def home():
    return Page(..., RefreshButton.for_region(status, href=...), status_panel())
```

- `app.region(id, *, selector=None, description=None)` returns a `FragmentRegion` (or thin wrapper)
  with default `selector=f"#{id}"`. Usable as `id=`, `target=`, and in `fragment_regions=`.
- `@app.fragment(path, *, region=|regions=)` registers a component/fragment route, merges declared
  regions into the route policy, and documents fragment intent in OpenAPI/registry metadata.
- `@app.page` / existing `@app.component` / `@app.action` remain; `@fragment` is sugar, not a second
  router.
- `RefreshButton.for_region(region, ...)` (and similar builtins) emit `hx-target` / swap defaults
  from the region object so authors do not retype selectors.
- Optional later: nested control under a region root may **infer** default target = that region,
  always overridable; inference must show in Explorer (see §3). **Not required for v1 of this RFC.**

### 2. `swap(...)` builders

Public helpers that return real `InteractionResult` instances:

| Helper | Intent |
|---|---|
| `swap(content, *, toast=None, …)` | Primary fragment body (+ optional toast/OOB helpers) |
| `swap_oob(content, *oob, …)` | Primary + out-of-band updates |
| `retarget(content, region, …)` | Approved retarget when policy allows |
| `redirect_htmx(url)` / compose `.redirect(...)` | `HX-Redirect` vs full navigation — documented |

- Advanced fields (`headers`, `policy`, multi-OOB) stay available on `InteractionResult` and on
  builder keyword args / chained methods.
- Builders never invent undeclared regions or weaken `InteractionPolicy`.
- Re-export from `hedron` beginner surface; guide examples prefer `swap` then show the envelope.

### 3. Dev-mode diagnostics and Explorer preview

**Runtime (dev / non-production profiles only for verbose bodies):**

- On `FragmentRegionError` / unauthorized target: stable code (e.g. `HED-HTMX-00xx`) plus message
  listing **declared** region selectors/ids for that route and the **requested** `HX-Target`.
- Optional HTML problem details or `HX-Trigger` debug event in Explorer-attached apps — never
  leak route maps or secrets in production profiles.

**Static / CLI:**

- `hedron check` (or route audit): controls whose `hx-target` / `for_region` does not match any
  declared region on the referenced route → diagnostic, not silent pass.

**Explorer:**

- For a selected control (e.g. `RefreshButton`): show method, path, target region, swap strategy,
  CSRF requirement, and declared-region set — “what will this click do?” before running the app.
- Link from verbose 403/dev responses into that panel when Explorer is mounted.

## Alternatives considered

1. **Implicit refreshable scopes / NiceGUI binding.** Rejected — second runtime; non-goal.
2. **Auto-expose every component as a fragment route.** Rejected — violates addressable/explicit
   exposure (RFC-0008).
3. **Only documentation improvements.** Insufficient; ceremony and opaque 403s are API issues.
4. **Replace `InteractionResult` with ad-hoc tuples.** Rejected — builders wrap the envelope; the
   type remains the contract for headers/OOB/policy.

## Security implications

- Fail-closed region auth remains default in all profiles.
- Verbose mismatch bodies and Explorer graphs are **dev-gated**; production returns existing
  opaque/safe errors.
- `@fragment` does not bypass CSRF on unsafe methods or expand `FragmentRegion` by inference
  without registration.
- `swap` cannot attach OOB targets outside the authorized set.

## Accessibility implications

Ergonomic APIs must preserve existing a11y contracts on builtins (`RefreshButton`, toast, live
regions). No new interaction model for end users — developer-facing only. N/A for new widgets.

## Performance implications

Negligible. Explorer preview is offline/registry metadata. Check is build/dev time.

## Testing strategy

- Unit: `region` defaults; `swap*` ↔ `InteractionResult` equality on headers/content/OOB.
- Integration: `@fragment` registers regions; undeclared target still 403 in production profile;
  dev profile includes diagnostic code + declared list.
- Explorer/CLI: snapshot or contract tests for preview payload and check diagnostics.
- Guide/scaffold: `hedron new` first interaction uses `region` + `@fragment` + `swap` or
  `for_region`.
- Compose with RFC-0036 marks and AppScenario HTMX helpers (#22–#26).

## Compatibility and migration

Additive. Existing `FragmentRegion` / `@component(..., fragment_regions=)` / raw
`InteractionResult` remain Supported. Docs and scaffold migrate to the ergonomic path; no required
app churn for 0.15.

## Accepted decisions (0.15)

1. **`@app.fragment`:** thin alias of `@app.component` with fragment-oriented defaults (not a second
   router).
2. **Builder surface:** `hedron.interaction.swap` (and siblings) re-exported from `hedron`.
3. **Production errors:** region mismatches stay compact/opaque; verbose declared-vs-requested
   bodies are dev/Explorer gated only.
4. **Parent-region target inference:** Deferred (not required for v1 acceptance).

## Acceptance criteria

- A status-panel interaction in the getting-started guide uses `region` + `@fragment` (or documented
  equivalent) and does not require hand-synchronizing three copies of the same id string.
- `swap(content)` is documented as the default return for fragment handlers; advanced guide section
  still shows `InteractionResult`.
- Production undeclared-target requests remain fail-closed; dev/Explorer paths expose declared vs
  requested targets via stable `HED-*` diagnostics.
- Explorer (with `hedron[dev]`) can explain method, path, target, and swap for a stock
  `RefreshButton.for_region` example.
- `hedron check` reports at least one class of target/region mismatch with remediation text.
- No acceptance of implicit widget state, auto-routed components, or client callback defaults.

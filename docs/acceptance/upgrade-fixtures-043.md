# Upgrade fixtures — phase 0.43 refreshable views and commands

**Status:** Planned  
**Baseline:** Published `v0.42.0`  
**Target:** `v0.43.0`  
**Owning gate:** `COMPAT-043`

Phase 0.43 is additive. The upgrade suite proves that a 0.42 application using the stable region
facade runs unchanged on 0.43 and that adopting handles can be performed one interaction at a time.

## Required fixture families

### Unchanged 0.42 application

The fixture uses:

- `app.region` and explicit host ids;
- `@app.fragment(..., region=...)` and `fragment_regions=`;
- `RefreshButton.for_region`;
- `swap`, `swap_oob`, `retarget`, `OobUpdate`, and direct `InteractionResult`;
- GET fragments, POST actions, form validation, toast, multi-OOB, status codes, cache/history,
  mounts, async dependencies, Flask, and Django equivalents.

Expected result: source, generated markup, response status/headers/body, target rejection, CSRF,
focus/fallback, and diagnostics retain the 0.42 contract except for explicitly documented additive
metadata.

### Side-by-side mixed application

One page uses legacy regions and refreshable handles simultaneously. An existing action may return
an `InteractionResult` while another command returns a refresh intent or `PatchSet`. Targets may not
cross accidentally; reserved sinks keep their current behavior.

Expected result: no duplicate route names/ids, no registry ambiguity, no target-policy widening,
and Explorer labels both authoring layers accurately.

### Mechanical single-view migration

Before:

```python
status = app.region("service-status")


def status_panel():
    return html.div("Healthy", id=status.id)


@app.fragment("/status", region=status)
def refresh_status():
    return swap(status_panel())


RefreshButton.for_region(status, href="/status")
```

After:

```python
@app.refreshable("/status", key="service-status")
def status():
    return StatusPanel("Healthy")


status()
status.refresh_button()
```

The explicit path/key preserve externally used URLs and DOM identity. The fixture checks equivalent
successful and rejected requests, host semantics, cache, focus, and no-JavaScript fallback claims.

### Mutation and multi-output migration

Before: an `@app.action(..., fragment_regions=...)` returns primary content plus `OobUpdate`.

After: an `@app.command` returns either:

```python
return refresh(notes, note_count)
```

or:

```python
return patches(notes.replace(...), note_count.update(...))
```

The fixture records the intentional difference: refresh intents perform normal follow-up GETs and
are not atomic; direct patches stay in one response. Documentation must not describe them as
equivalent performance/transaction behavior.

### Bound routes

Parameterized component/action routes migrate to `bind(...)`. Fixtures cover path converters,
query parameters, Unicode, mount prefixes, repeated instances, missing/extra parameters, secret
redaction, and stable explicit instance keys. The fixture distinguishes 0.43 structural failures
(unknown/missing names, unsafe serialization/encoding, identity conflicts) from full typed request
validation, which remains the normal GET route's responsibility.

### Phase 0.44 handoff baseline

The fixture freezes the intentional predecessor seam before 0.43 cuts:

- `FragmentHandle[Bind, Content]` and `ActionHandle[Input, Result]` have two generic slots in the
  documented order; `BoundFragment[Content]` and `Patch[Content]` keep one content slot;
- runtime, Explorer, CLI, scenarios, and conformance read the same versioned base handle descriptor
  and fingerprint;
- the structural binding adapter is replaceable only through its documented protocol;
- `Form(action=handle, ...)` wires explicit fields and no `ActionHandle.form()` exists;
- command effects are labeled `dynamic` or `observed`, never inferred as declared;
- namespaced descriptor extensions cannot override base route, identity, ownership, host, target,
  fallback, limits, or response conversion.

A test-only model adapter, `TypeSchema` extension, generated-form consumer, and declared-effect
extension attach to this fixture. They may narrow validation and enrich tooling, but the base
request/response/markup/authorization goldens stay unchanged. This proves the seam without shipping
0.44 public features in 0.43.

### Testing migration

Legacy raw client/header/OOB assertions and new handle-based `AppScenario` assertions run against
the same application and agree on status, rendered content, target, refresh/patch outputs, and
errors.

## Rollback

Rollback to 0.42 requires retaining the original low-level route implementation or reverting the
additive handle commit. There is no compatibility shim that makes 0.43-only decorators importable
on 0.42. Data/storage migrations are not required by this phase.

Generated paths and ids are intentionally not rollback contracts. Applications that need source- or
version-stable values must use explicit `path=` and `key=` before cutover.

## Evidence required at cut

- source fixtures for every family above;
- golden request/response/markup and registry metadata;
- generic-arity, base-descriptor/fingerprint, structural-adapter, dynamic-effect, and 0.44 handoff
  fixtures;
- FastAPI/Flask/Django conformance output;
- 0.42 and 0.43 environment lock files;
- migration and rollback commands;
- a review ledger for every intentional difference;
- confirmation that no 0.42 stable symbol was deprecated or removed.

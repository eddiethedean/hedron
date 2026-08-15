# Upgrade fixtures — phase 0.44 type-driven authoring

**Status:** Planned<br>
**Planning baseline:** Published `v0.42.0`<br>
**Required predecessor/cut baseline:** Verified `v0.43.0`<br>
**Target:** `v0.44.0`
**Owning gate:** `COMPAT-044`

Phase 0.44 is additive and opt-in. The upgrade suite proves that existing annotations are not
reinterpreted, that 0.43 function handles run unchanged, and that boundary models, generated forms,
effect declarations, outcomes, and class handlers can be adopted independently.

## Required fixture families

### Unchanged Published 0.42 application

The fixture exercises explicit FastAPI routes/dependencies/models, `Form`/`AutoForm`/`Action`,
regions, fragments, `InteractionResult`, Flask, Django, Jinja, OpenAPI, Explorer, and scenario
tests. It includes ordinary `Annotated` metadata from FastAPI and a third-party library.

Expected result: source, imports, dependency injection, request parsing, form behavior, schemas,
markup, status/headers, security, errors, and diagnostics retain the 0.42 contract. No 0.44 marker
is inferred and third-party metadata is not invoked by Hedron.

### Unchanged phase 0.43 application

The fixture uses function `@app.refreshable` and `@app.command` handlers, `bind`, handle controls,
`refresh`, direct patches, fallbacks, generated/explicit paths/keys, and raw 0.43 scenario helpers
without 0.44 boundary models.

Expected result: it runs unchanged. Its fixed generic arity and coarse mapping input slots remain
valid; no precision or behavior changes merely because ordinary annotations are present.
Validation, routing, responses, markup, explicit forms, dynamic/observed effects, and errors do not
change.

### Verified 0.43 handoff preservation

The exact 0.43 predecessor fixture is rerun after 0.44 installation. It asserts:

- the same generic slot count/order and runtime handle classes;
- the same base descriptor version fields/fingerprint authority;
- unmodeled handlers still use structural binding and normal-GET validation;
- explicit `Form(action=handle, ...)` markup/action/method/CSRF/fallback is unchanged;
- commands without effect markers remain dynamic and observations remain non-declarative;
- base route, identity, ownership, host, target, limits, fallback, and response goldens are
  unchanged; and
- absent/unknown type extensions do not affect base behavior.

Modeled fixtures then attach a Pydantic binding adapter and fingerprint-bound `TypeSchema`
extension. Only the opted-in validation/form/effect/tooling projections change.

### Incremental view-parameter model

Before:

```python
@app.refreshable("/users/{user_id}")
def user_card(user_id: UUID, tab: str = "overview", actor=Depends(current_user)):
    ...

card = user_card.bind(user_id=user.id, tab="activity")
```

After:

```python
class UserCardParams(BaseModel):
    user_id: UUID
    tab: Literal["overview", "activity"] = "overview"


@app.refreshable("/users/{user_id}")
def user_card(
    params: Annotated[UserCardParams, ViewParams()],
    actor: Annotated[User, Depends(current_user)],
):
    ...
```

The fixture proves equivalent route/host identity and request results for valid values, improved
model validation for invalid values, and absolute separation between bindable fields and injected
`actor`. The Pydantic adapter implements the 0.43 binding protocol and uses documented FastAPI
request registration; no second reversal/identity/request parser exists. It covers aliases,
Unicode, query repetition, strictness, extras, sensitive values, `InstanceKey`, mounts, and
rollback.

### Incremental command form

An explicit hand-built form and a `FormBody` model/generated form submit to the same command
semantics. Fixtures disposition strings, numbers, booleans, enums, dates, UUIDs, optional fields,
bounded collections, files, nested values, and discriminated unions.

Expected result: supported generated controls match server parsing, validation, CSRF, encoding,
fallback, error association, safe value retention, and HTMX/no-JS outcomes. Unsupported fields fail
generation and succeed through an explicit control/form override.

### Declared effects

An existing command returning `refresh(notes, note_count)` is annotated with
`Refreshes(notes, note_count)`. The declared and undeclared forms have equivalent successful
behavior. Negative fixtures return an extra target, foreign handle, direct patch under a refresh
declaration, duplicate/excessive targets, and a dynamic target.

Expected result: declarations validate explicit outputs and improve tooling graphs; they never
execute refreshes, authorize targets, or discover data dependencies.

### Typed outcomes

An explicit command branch returning success/conflict validation responses migrates to a
discriminated Pydantic outcome plus complete `OutcomeMap`. Fixtures cover every variant, invalid
discriminator, wrong return type, incomplete/duplicate maps, renderer failure, status/fallback,
declared effects, safe errors, and rollback to explicit results.

Expected result: mapped behavior is equivalent for valid variants and fails safely for contract
violations. Arbitrary `BaseModel` returns remain unsupported without a mapping.

### Function/class equivalence

A function refreshable view and `RefreshableView` class share the same params/data/content. A
function command and `CommandHandler` class share the same input/outcome/effects.

Expected result: route, handle, schema, markup, validation, DI, CSRF, response, errors, tracing,
Explorer, scenarios, cancellation, and fallback agree. Shared mutable request state is rejected;
the documented request-scoped factory passes concurrency/teardown fixtures.

### Static and dynamic tooling

Static CLI inspection runs against a fixture containing import side effects that would fail if
executed. It reports syntactic markers and unresolved runtime facts without importing the project.
Explicit dynamic inspection imports a trusted app and yields the complete redacted schema.

Expected result: no static execution, no secret leakage, and clear fact provenance/mode labels.

### Adapter and template projection

Portable schema/effect/outcome fixtures run on FastAPI, Flask, Django, conformance, and Jinja
surfaces. FastAPI DI remains the flagship. Any adapter gap is machine-labeled with reason, owner,
and destination rather than approximated silently.

## Rollback

Rollback to 0.43 replaces boundary model parameters with the prior explicit handler signature,
uses explicit forms, removes effect declarations/outcome maps, and registers equivalent function
handlers. Public routes/keys and application data do not require migration.

Rollback to 0.42 additionally follows the 0.43 handle-to-region fixtures. Generated form markup,
`TypeSchema`, class handler identities, and implicit model fingerprints are not rollback contracts.
Applications needing stable external URLs, field names, or DOM identity must keep explicit values.

## Evidence required at cut

- source and locked environments for every fixture family;
- request/response/markup/schema/diagnostic goldens with redaction review;
- mypy and pyright output;
- three-engine a11y/no-JS form results;
- function/class concurrency and teardown results;
- FastAPI/Flask/Django/Jinja capability report;
- performance comparison to the recorded 0.43 equivalent paths;
- migration and rollback commands with intentional-difference ledger;
- confirmation that no 0.42/0.43 public symbol was removed, deprecated, or behaviorally
  reinterpreted without opt-in.

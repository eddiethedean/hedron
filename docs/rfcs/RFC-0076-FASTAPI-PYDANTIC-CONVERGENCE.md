# RFC-0076: FastAPI and Pydantic convergence

**Status:** Accepted<br>
**Target phase:** 0.49 (`v0.49.0`)<br>
**Decision:** D-081<br>
**Stage 0 contract refine:** D-084<br>
**Planning baseline:** Published in-tree `v0.48.0` (D-084; original Stage 0 baseline was Published in-tree `v0.46.0`)<br>
**Required predecessor/cut baseline:** Verified in-tree `v0.48.0`<br>
**Tracking:** [#380](https://github.com/eddiethedean/hedron/issues/380)<br>
**Upstream baseline:** FastAPI `>=0.121.0,<0.150`; Pydantic `>=2.12.0,<2.15` (D-118)<br>
**Extends:** RFC-0001, RFC-0002, RFC-0004, RFC-0008, RFC-0009, RFC-0012,
RFC-0013, RFC-0015, RFC-0016, RFC-0019, RFC-0020, RFC-0021, RFC-0024,
RFC-0026, RFC-0028, RFC-0040, RFC-0043, RFC-0049, RFC-0053, RFC-0064,
RFC-0065, RFC-0066, RFC-0070, RFC-0071, RFC-0072, RFC-0073, and RFC-0075

**Revision:** 2026-08-17 — D-084 contract refine against Published in-tree `v0.48.0`:
planning baseline rebased; lifetime, binding, TypeSchema v2, unions/OpenAPI/scopes,
and settings/research locks recorded; FailFast moved off the adapter gate; real 0.43–0.48
handles, TypeSchema v1, expanded-field signatures, `HedronRouter`, `install_openapi`, and
HTMX SSE seams named. No runtime or version claim.

## Summary

Phase 0.49 converges Hedron's manual FastAPI/Pydantic integration with the strongest stable
features of its pinned upstreams. It does not make Hedron a transparent wrapper around either
library. Instead, it introduces an inspectable compilation plan that selects native FastAPI
parameter binding where semantics match, retains Hedron's portable fallback where they do not,
and produces separate sanitized validation and serialization projections from Pydantic.

The phase adds explicit dependency lifetimes, tagged wire unions, richer OpenAPI responses and
security/callback facts, preserved router provenance, cached validation adapters for selected hot
boundaries, and deployment-settings evaluation. Experimental partial validation and missing-value
semantics remain quarantined research; convenience features that would weaken deterministic
authority or secret safety are explicitly excluded.

## Goals

- Model handler-scoped versus response-scoped `yield` dependency lifetimes and diagnose invalid or
  wasteful use across ordinary, streaming, SSE, download, and background-work paths.
- Add a deterministic binding-strategy compiler that uses native Pydantic query/header/cookie/form
  models when equivalent and retains field expansion for path mixtures, file uploads, portability,
  or unsupported shapes.
- Split `TypeSchema` into sanitized validation/input and serialization/output projections, with
  write-only/read-only/shared dispositions and independent fingerprints.
- Require stable discriminators for new multi-variant wire payloads and migrate selected events,
  outcomes, updates, manifests, MCP, and remote-adapter envelopes.
- Exploit preserved `APIRouter`/`APIRoute` identity for nested package provenance, late pre-seal
  registration, diagnostics, and OpenAPI without relying on upstream alpha matching hooks.
- Project typed status responses, media types, headers, callbacks, webhooks, authorization
  requirements, and stable operation ids into OpenAPI while application code stays authoritative.
- Lock strict JSON content-type behavior and expose deviations in production diagnostics.
- Add a portable `RequiresScopes` declaration compiled by the FastAPI adapter to OpenAPI security
  and by other adapters to their existing guard seams; scopes never replace object/tenant authz.
- Reuse compiled `TypeAdapter` instances at measured transport/manifest/data boundaries while
  preserving duplicate-key rejection, size limits, and deterministic error policy.
- Evaluate `pydantic-settings` only for deployment packages against existing provenance,
  precedence, redaction, import-time, digest, and rollback requirements.
- Run quarantined research for streamed partial validation, missing-value PATCH semantics, and
  `FailFast`, without adding them to the Supported public surface unless separately admitted.

## Non-goals and exclusions

- Replacing Hedron models, `SafeUrl`, security policy, binding authority, catalogs, manifests, or
  portable Flask/Django semantics with raw upstream objects.
- Automatic inference of authorization, OAuth providers, scope grants, webhook delivery, retry,
  durable outboxes, database ownership, transactions, or background execution.
- Depending on FastAPI alpha `APIRouter.matches()` / `.handle()` customization.
- Using `SerializeAsAny` at security boundaries, serialization context for authorization,
  `validate_call` as a handler runtime, computed fields as writable form fields, Pydantic network
  URLs in place of purpose-specific `SafeUrl`, or FastAPI Cloud as a deployment contract.
- Treating partial validation, Pydantic's experimental `MISSING`, or `FailFast` as default form,
  action, persistence, or authorization behavior.
- Removing the existing structural binding adapter, changing non-opted-in routes, requiring
  Pydantic in portable runtimes beyond current contracts, closing `SR-021`, or scheduling `1.0`.

## Proposed design

### Dependency lifetime plan

`DependencyLifetime` is `handler` or `response`. The FastAPI adapter compiles these to
`Depends(scope="function")` and `Depends(scope="request")`. A `DependencyPlan` records resource
identity, lifetime, streaming use, dependency edges, cleanup order, and portability disposition.
Response-scoped parents may not depend on a shorter-lived child. Streaming/SSE/download routes
that consume a yielded resource after handler return require response lifetime. Ordinary routes
receive handler lifetime by default when compatibility and evidence allow it.

Background work may not capture request-owned resources. Diagnostics identify resources retained
through response transmission and offer explicit remediation rather than silently changing an
application dependency.

### Binding strategy compiler

`BindingStrategy` is `native-model` or `expanded-fields`. Query-only, header-only, cookie-only, and
non-file form models may compile to FastAPI's native Pydantic parameter-model bindings. Mixed path
and query models, multipart/file forms, incompatible aliases, and portable adapter cases use the
existing expanded-field signature plus `PydanticBindingAdapter`.

The compiler emits a `BoundaryBindingPlan` containing source, model identity/fingerprint, strategy,
field locations, aliases, extra-field policy, content type, adapter disposition, and fallback
reason. Both strategies must produce equivalent validated models, errors, OpenAPI, catalogs,
scenarios, CSRF behavior, and Flask/Django outcomes for the locked fixture inventory.

### Dual schema projections

`TypeSchema` v2 adds `input_projection`, `output_projection`, `shared_fields`, `write_only_fields`,
`read_only_fields`, and separate fingerprints. Pydantic validation and serialization schemas are
generated through a Hedron-owned `GenerateJsonSchema` policy and reduced to a closed inert subset.
Unknown keywords, callables, executable extensions, secrets/default values/examples, and
unsupported recursion fail closed or receive an explicit disposition.

Computed fields and serializers may appear only in the output projection. Secrets are write-only
or excluded and never become examples/defaults. The compiler preserves the v1 TypeSchema reader
during the compatibility window and provides deterministic upgrade fixtures.

### Tagged wire unions

New public wire unions use a stable literal discriminator, normally `kind`. Initial migrations
cover selected interaction outcomes, typed updates, browser/server events, job messages, package
projection entries, MCP envelopes, and remote-adapter descriptors. Each migration retains schema
version, unknown-kind failure, payload bounds, redaction, cross-runtime fixtures, and existing
Python constructors where compatible.

Untagged unions remain valid for ordinary application models, but tooling warns when a public
wire/catalog schema relies on Pydantic smart-union selection.

### Router provenance and OpenAPI

Nested `HedronRouter` instances retain identity and provenance through inclusion. Package/feature
origin, security requirements, descriptor fingerprints, and late pre-seal routes remain attached
to the actual route. Registration after catalog or OpenAPI seal is rejected deterministically.

OpenAPI projection describes every declared response status, media type, HTMX header, SSE stream,
download, validation fragment, conflict, auth failure, and rate-limit response. Callback and
webhook schemas document application-owned integrations but do not deliver them. Stable operation
ids remain locked for client generation. JSON endpoints retain native response models and
Pydantic-backed serialization; HTML endpoints continue using response classes and `response_model`
suppression where required.

`RequiresScopes` declares public scope names and adapter requirements. It is projected into FastAPI
security dependencies/OpenAPI and portable adapter facts, but live authentication, tenant scope,
object authorization, and denial remain application-owned.

### Validation adapters and settings

Selected hot boundaries may use cached `TypeAdapter` instances and direct `validate_json()` after
benchmarking. Candidate boundaries include WebSocket messages, MCP envelopes, job/cache records,
build manifests, remote-adapter metadata, and bounded data batches. Existing duplicate-key checks,
size/depth limits, canonical encoding, and redaction run before or alongside validation.

`pydantic-settings` is evaluated only for `fastapi-workbench`, `hedron-workbench`, and
`hedron-posit`. Adoption requires exact source precedence, provenance, unknown-key rejection,
secret redaction, deterministic digests, no surprising filesystem/network/import-time reads, and
backward-compatible environment behavior. Otherwise the existing loaders remain authoritative.

### Experimental research

- Partial validation may render clearly provisional streamed model output, followed by mandatory
  complete validation before persistence, action, authorization, or canonical UI state.
- PATCH research compares a Hedron-owned stable unset value/state with Pydantic's experimental
  `MISSING`; the experimental sentinel cannot enter the public Supported API in this phase.
- `FailFast` is measured only for whole-batch-rejected adversarial ingestion where losing later
  error details is acceptable; it remains off for forms/configuration.

Research produces dispositions and evidence, not an obligation to ship runtime APIs.

## Security implications

- Strict JSON content types are tested and strict production profiles reject unreviewed opt-out.
- Native and expanded binding share the same URL, selector, secret, CSRF, extra-field, size, and
  injected-name policies.
- Schema projections contain no secret values, callable bodies, request data, ambient settings, or
  subclass-only fields. `SerializeAsAny` is prohibited at protected boundaries.
- Scopes are non-authoritative declarations; all live authn/authz checks still run.
- Callbacks/webhooks are documentation unless an application supplies its own authenticated,
  signed, durable delivery system.
- Validation adapters preserve duplicate-key, depth, count, byte, and error-redaction controls.

## Accessibility implications

Dual projections must retain titles, descriptions, required/optional/read-only/write-only state,
constraints, and error paths used by generated forms and Explorer. Binding-strategy changes must
not alter focus, error summaries, field associations, or progressive enhancement. Computed output
fields require meaningful labels and cannot silently become interactive controls.

## Performance implications

The phase records schema compile/startup time, route inclusion and OpenAPI time, request binding,
JSON validation/serialization, adapter construction, streaming resource hold time, memory, and
error-path budgets. Cached adapters and tagged unions are adopted only with measured benefit.
Applications not using typed authoring or the evaluated deployment packages incur no new runtime
dependency or request-path work.

## Compatibility and migration

Existing direct FastAPI, expanded-field, structural binding, Flask, Django, HTML response, and
OpenAPI extension behavior remains supported. `TypeSchema` v1 has a documented read/upgrade window.
Every optimized path retains an explicit fallback and rollback. Upstream minor ranges remain
bounded; no alpha API becomes foundational.

## Resolved questions (D-081)

1. **Which gates?** Closed inventory `LIFETIME-049`, `BINDING-049`, `SCHEMA-049`,
   `UNION-049`, `ROUTER-049`, `OPENAPI-049`, `SECURITY-049`, `ADAPTER-VALIDATION-049`,
   `SETTINGS-049`, `RESEARCH-049`, `A11Y-049`, `PERF-049`, `COMPAT-049`, `DOCS-049`,
   `REGRESS-049`, and `PKG-049`. Do not split SCHEMA vs UNION or park TypeSchema v2 later.
2. **Does Hedron wrap FastAPI/Pydantic transparently?** No. Native adoption is an
   inspectable compilation plan with expanded-fields fallback and portable authority.
3. **May settings or research ship without a disposition?** No. `SETTINGS-049` and
   `RESEARCH-049` may conclude with adopt/retain/defer/exclude; unadmitted experimental
   features cannot appear in the Supported inventory.
4. **What is the release baseline?** Verified 0.48 is required before Stage 1 or the
   0.49 cut. Original Stage 0 planning baseline was Published in-tree `v0.46.0`.
   **D-084** rebases the living/planning baseline to Published in-tree `v0.48.0`.

## Resolved questions (D-084)

1. **Does 0.49 still include all 16 gates?** Yes. The D-081 list remains in scope.
   `SETTINGS-049` and `RESEARCH-049` may finish as explicit dispositions. Do not split
   SCHEMA vs UNION and do not park TypeSchema v2 later.
2. **Does this refine change a later phase or the living tip?** No. Cut target stays
   `v0.49.0`. Living tip stays `v0.48.0`. Do not reopen 0.48, `polling_only`,
   `MORPH-048`, `SR-021`, or schedule `1.0`.
3. **Which shipped seams does 0.49 consume?** `TypeSchema` v1 under `hedron.type`
   (`schema_version=1`, `attach_type_schema`, `type_schema_from_descriptor`,
   `TypeSchema.stable_fingerprint()`; forbidden keys `values`/`defaults`/`examples`/
   `callbacks`/`request`/`model`). Structural bind:
   `BindingPlan` / `BindingAdapter` / `StructuralBindingAdapter` /
   `PydanticBindingAdapter` / `apply_modeled_signature`. Markers:
   `ViewParams` / `FormBody` / `Sensitive` / `InstanceKey` / `Control` /
   `Refreshes` / `Updates` and `OutcomeMap(case(...), ...)`. Handles:
   `FragmentHandle[BindT, ContentT]`, `ActionHandle[InputT, ResultT]`,
   `BoundFragment[ContentT]`, `Patch[ContentT]`, `BaseHandleDescriptor`
   (`kind` `view`/`command`, `version=1`). `descriptor_fingerprint` does **not** hash
   `effect` or `extensions`. Router/OpenAPI: `HedronRouter(APIRouter)`, `HedronRoute`,
   `install_openapi`, `operation_id_for`. Catalog:
   `Hedron.include_component` / `include_feature` / `interactions`,
   `compile_interaction_catalog` / `seal_app_catalog` after `seal_registry`.
   0.48 HTMX: `Page.htmx_extensions`, `SseRegion` / `SseTrigger`, experimental SSE
   helpers — LIFETIME consumers only. Flask/Django stay `projection_adapter` /
   TypeSchema `bounded_exception` stacked on
   [adapter-disposition-044.toml](../acceptance/adapter-disposition-044.toml) and
   [host-portable-facts-045.toml](../acceptance/host-portable-facts-045.toml).
   Pins: FastAPI `>=0.121.0,<0.150` (Supported CI still `<0.142`), Pydantic
   `>=2.12.0,<2.15`, Python 3.10–3.14 (broadened for 1.0 by D-118).
   `Depends(scope=...)` exists since FastAPI 0.121.
4. **How do Hedron lifetime names map to FastAPI scopes?** Public Hedron values stay
   `handler` / `response`. FastAPI values are `function` / `request`, not `response`.
   `DependencyLifetime.HANDLER` → `Depends(scope="function")`.
   `DependencyLifetime.RESPONSE` → `Depends(scope="request")` (exit after the response
   is sent). Ordinary routes default to HANDLER when evidence allows;
   streaming/SSE/download that still need the resource after handler return require
   RESPONSE. Background work must not capture either request-owned value (D-020).
   User-authored FastAPI `Depends()` remains valid; `DependsOn` is additive.
   Portable `DependencyLifetime` / `DependencyPlan` live in `hedron-core`; compilation
   lives in `hedron`. Flask/Django record disposition only. Lock:
   [fastapi-lifetime-049.toml](../acceptance/fastapi-lifetime-049.toml).
5. **Is `BoundaryBindingPlan` a rename of `BindingPlan`?** No. `BindingPlan` stays the
   0.43 structural path/query plan. `BoundaryBindingPlan` is new (`native-model` or
   `expanded-fields`, fingerprint, fallback reason). Native-model is allowed only for
   query-only, header-only, cookie-only, and non-file form models when FastAPI native
   Pydantic parameter-model behavior is equivalent. Mixed path/query, multipart/file,
   incompatible aliases, and portable adapters keep expanded-fields via
   `apply_modeled_signature`. Existing `ViewParams`/`FormBody` routes keep expanded
   behavior unless equivalence is proven or the author forces the portable fallback.
   Flask/Django never receive FastAPI native-model. Lock:
   [fastapi-binding-049.toml](../acceptance/fastapi-binding-049.toml).
6. **Is TypeSchema v2 a replacement payload?** No. Keep
   [type-schema-044.toml](../acceptance/type-schema-044.toml). v2 adds
   `input_projection`, `output_projection`, shared/read-only/write-only classification,
   and separate TypeSchema-internal fingerprints. Pydantic owns JSON Schema generation;
   Hedron sanitizes to a closed inert subset. OpenAPI authority stays FastAPI. Today's
   `TypeSchema.__post_init__` fail-closes on `schema_version != 1`; v1 readers remain
   during the compatibility window; Stage 1 implements dual-version load; Stage 0 does
   not bump `TYPE_SCHEMA_VERSION`. Dual-projection fingerprints are not a second
   `descriptor_fingerprint`. Lock:
   [typeschema-v2-049.toml](../acceptance/typeschema-v2-049.toml).
7. **What are the tagged-union and OpenAPI rules?** New public **wire** unions use
   literal discriminator `kind`. `CatalogEntry.kind` stays `view`/`command`. Lock
   migration **families** now (exact symbols in Stage 1): `OutcomeMap` results, typed
   updates, selected event envelopes, job messages, MCP envelopes, remote-adapter
   descriptors. Untagged application models stay valid; tooling warns when a public
   catalog/wire schema relies on smart-union selection. Nested `HedronRouter` identity
   is the existing `APIRouter` subclass. Exclude FastAPI alpha `APIRouter.matches()` /
   `.handle()`. Late registration is legal only before `seal_registry` /
   `seal_app_catalog` / OpenAPI cache. HTML routes keep response-class + `text/html`
   injection; JSON routes may keep native response models. `RequiresScopes` is a
   portable declaration compiled to FastAPI Security/OpenAPI and adapter facts; it does
   not grant or replace live authz. Strict JSON content-type extends
   `reject_json_formbody` 415 under security profiles — not a new CSRF protocol. Lock:
   [fastapi-unions-openapi-049.toml](../acceptance/fastapi-unions-openapi-049.toml).
8. **Where does FailFast live?** `ADAPTER-VALIDATION-049` is measured cached
   `TypeAdapter` / `validate_json()` only. Candidates: WebSocket messages, MCP
   envelopes, job/cache records, build manifests, remote-adapter metadata, bounded data
   batches. **Not** the FormBody request path. **FailFast belongs entirely to
   `RESEARCH-049`.** Remove it from adapter `adopt_if_measured`.
9. **Which settings packages?** Only `fastapi-workbench`, `hedron-workbench`, and
   `hedron-posit`. Today they use argparse / `WorkbenchConfig` and custom loaders, not
   `pydantic-settings`. Do **not** evaluate `hedron.config.HedronSettings`. Default
   until a Stage 1 spike: Evaluate, likely `retain-custom-loader`. Stage 0 adds no
   dependency. Research stays quarantined: partial streamed validation (complete
   validation before persist/action/authz/canonical UI), Hedron-owned unset vs
   experimental Pydantic `MISSING`, and FailFast for whole-batch-reject only. Lock:
   [fastapi-settings-research-049.toml](../acceptance/fastapi-settings-research-049.toml).
10. **Where do symbols live?** Portable plans, scopes, and schema fields in
    `hedron-core` (no FastAPI). Compiler, `DependsOn`, native-model eligibility, and
    OpenAPI projection in `hedron`. No new package. Optional namespaced
    `PackageProjection` is allowed; plans are not a new `CatalogEntry.kind` and not a
    fourth fingerprint.
11. **Which diagnostic family?** Keep `HED-TYPE-0001`–`0010`. Reserve `HED-FP-*` in
    docs only. Do not assign new numbers during this refine.
12. **What does Stage 1 still own?** Numeric limits, exact union-symbol inventory,
    adapter microbenchmarks, pydantic-settings spike evidence, any Supported FastAPI
    matrix expansion, tracking-issue-bound runtime, and dual-version TypeSchema load.
    Do not invent those numbers here.
13. **May Stage 1 start before the 0.48 PyPI/Git tag?** Yes for in-tree Verified 0.48
    evidence. Tracking issue [#380](https://github.com/eddiethedean/hedron/issues/380)
    is bound. Do not wait on `#373` publish assets. Do not start Stage 1 during this
    contract refine.

## Acceptance criteria

`LIFETIME-049`, `BINDING-049`, `SCHEMA-049`, `UNION-049`, `ROUTER-049`, `OPENAPI-049`,
`SECURITY-049`, `ADAPTER-VALIDATION-049`, `SETTINGS-049`, `RESEARCH-049`, `A11Y-049`,
`PERF-049`, `COMPAT-049`, `DOCS-049`, `REGRESS-049`, and `PKG-049` satisfy the release gate.
Settings and research gates may conclude with explicit retain/defer/exclude dispositions; no
unadmitted experimental feature may appear in the Supported inventory.
The `v0.49.0` cut contains no Deferred row hidden inside a Supported claim.

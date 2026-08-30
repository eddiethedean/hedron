# FastAPI/Pydantic convergence implementation plan (phase 0.49)

**Status:** Published as in-tree `v0.49.0` (tag/PyPI deferred). Human AT (`SR-021`) stays open.<br>
**Tracking:** [#380](https://github.com/eddiethedean/hedron/issues/380)<br>
**Decision/RFC:** D-081, refined by D-084 / [RFC-0076](../rfcs/RFC-0076-FASTAPI-PYDANTIC-CONVERGENCE.md)<br>
**Planning baseline:** Published in-tree `v0.48.0`<br>
**Target:** Hedron `v0.49.0`<br>
**Required predecessor:** Verified `v0.48.0`

Stage 1 compiled those plans as in-tree `v0.49.0`. FailFast stays research.

## Consume shipped, do not fork

- `hedron_core.type_schema.TypeSchema` / `attach_type_schema` /
  `type_schema_from_descriptor` / `TYPE_SCHEMA_VERSION = 2` (v1 readers remain) /
  namespace `hedron.type`. Forbidden keys already include `values`, `defaults`,
  `examples`, `callbacks`, `request`, `model`.
- `hedron_core.updates.BindingPlan` / `BindingAdapter` /
  `StructuralBindingAdapter` and `hedron.type_authoring.adapter.PydanticBindingAdapter`.
  Field expansion: `hedron.type_authoring.signature.apply_modeled_signature` /
  `reconstruct_kwargs` / `reject_json_formbody`.
- Closed markers `ViewParams` / `FormBody` / `Sensitive` / `InstanceKey` /
  `Control` / `Refreshes` / `Updates` and `OutcomeMap(case(...), ...)`.
- 0.43–0.46 handles, `BaseHandleDescriptor` (`kind` `view`/`command`, `version=1`),
  `descriptor_fingerprint` (does **not** hash `effect` or `extensions`),
  `Hedron.include_component` / `include_feature` / `interactions`,
  `compile_interaction_catalog` / `seal_app_catalog` after `seal_registry`,
  `InteractionCatalog` / `CatalogEntry` / `PackageProjection`, `FeatureBundle`
  (not an executor). Flask/Django remain `projection_adapter`.
- `HedronRouter(APIRouter)`, `HedronRoute`, `hedron.openapi.install_openapi` /
  `operation_id_for`.
- 0.48 HTMX: `Page.htmx_extensions`, `SseRegion` / `SseTrigger`, experimental
  SSE helpers. Use them only as LIFETIME streaming/SSE consumers. Do **not**
  reopen `polling_only` or `MORPH-048`.
- FastAPI `>=0.121.0,<0.150` (Supported CI still `<0.142`); `Depends(scope=)`
  since 0.121. Pydantic `>=2.12.0,<2.15` (D-118). Deployment settings today: argparse
  `WorkbenchConfig` / custom loaders — no `pydantic-settings`.
- `hedron.config.HedronSettings` is **not** a `SETTINGS-049` candidate.

Lock files: [fastapi-lifetime-049.toml](../acceptance/fastapi-lifetime-049.toml),
[fastapi-binding-049.toml](../acceptance/fastapi-binding-049.toml),
[typeschema-v2-049.toml](../acceptance/typeschema-v2-049.toml),
[fastapi-unions-openapi-049.toml](../acceptance/fastapi-unions-openapi-049.toml),
[fastapi-settings-research-049.toml](../acceptance/fastapi-settings-research-049.toml).

## Architecture

The implementation has five one-way layers:

1. Portable lifetime, binding, schema, scope, response, and disposition values in `hedron-core`.
2. Pydantic compilation in `hedron`, producing sanitized plans without executing handlers.
3. FastAPI route/dependency/OpenAPI projection using documented stable APIs.
4. Flask/Django and package projection over the same portable plans.
5. Explorer/CLI/scenario/conformance evidence that never becomes runtime authority.

Authority stays 0.43 descriptor → 0.44 TypeSchema → 0.45 catalog. 0.49 compiles
those plans onto FastAPI; it does not add a fourth fingerprint or a new
`CatalogEntry.kind`.

HDJ and Explorer consume TypeSchema/catalog facts. They never become runtime
authority.

## Work packages

### M1 — Baseline and inventories

- Lock FastAPI/Pydantic/Starlette/Python matrices and all stable versus alpha/experimental APIs.
- Capture current route signatures, OpenAPI, TypeSchema, errors, lifecycle, adapter, startup, and
  request benchmarks.
- Produce exact model-shape, transport, settings-source, and response inventories.

### M2 — Dependency lifetimes

- Define `DependencyLifetime` and `DependencyPlan` in portable core.
- Compile FastAPI `HANDLER` → `Depends(scope="function")` and
  `RESPONSE` → `Depends(scope="request")`.
- Add streaming/SSE/download/background capture diagnostics and fixtures.
- Preserve user-authored FastAPI dependencies and provide explicit no-inference fallback.

### M3 — Binding strategy

- Define `BoundaryBindingPlan` beside existing `BindingPlan`; do not overload the 0.43 plan.
- Implement query/header/cookie/form native-model compilation.
- Retain expanded path/query/file/multipart and portable-adapter paths via
  `apply_modeled_signature`.
- Prove model/error/OpenAPI/CSRF/alias/extra parity across strategies and adapters.

### M4 — Dual TypeSchema

- Introduce TypeSchema v2 additive projections and fingerprints on the 0.44 payload.
- Implement a closed Hedron JSON-schema generator and sanitizer.
- Classify shared/read-only/write-only/computed/secret/unsupported fields.
- Add v1 read/upgrade, static tooling, catalog/manifest/MCP/Gradio consumers, and rollback.
- Do not bump `TYPE_SCHEMA_VERSION` until dual-version load exists.

### M5 — Tagged unions and adapters

- Inventory public wire unions and migrate a bounded representative set.
- Cache TypeAdapters per type/version boundary and measure direct JSON validation.
- Preserve duplicate-key, size/depth/count, redaction, and canonical encoding policy.
- Keep FailFast on `RESEARCH-049`.
- Add Node/Java/cross-runtime fixtures for tags, unknown variants, and errors.

### M6 — Router and OpenAPI convergence

- Record nested router/package/feature provenance on preserved route objects.
- Support late registration only before registry/catalog/OpenAPI seal.
- Project responses, media types, headers, callbacks/webhooks, security requirements, operation ids,
  input/output schemas, SSE, downloads, and HTMX metadata.
- Keep alpha matching/handling hooks out of runtime code.

### M7 — Security scopes and strict content types

- Define portable `RequiresScopes` and adapter disposition.
- Compile FastAPI OpenAPI/security metadata without replacing application authz.
- Extend `reject_json_formbody` 415 under security profiles; not a new CSRF protocol.
- Add adversarial scope-confusion, content-type, schema leak, and callback overclaim cases.

### M8 — Settings evaluation

- Spike pydantic-settings in Workbench/Posit packages only.
- Compare source precedence/provenance, unknowns, secrets, digests, import I/O, paths, and rollback.
- Adopt per package only if all compatibility and operations requirements pass; otherwise record
  `retain-custom-loader`.
- Do not evaluate `hedron.config.HedronSettings`.

### M9 — Experimental research

- Prototype provisional LLM stream validation with mandatory final validation.
- Compare stable Hedron unset state to experimental Pydantic `MISSING` for PATCH.
- Benchmark `FailFast` for reject-whole-batch ingestion.
- Publish disposition; do not leak experimental types into Supported signatures or schemas.

### M10 — Evidence and cut

- Complete browser, adapter, security, accessibility, performance, package, upgrade, and rollback
  matrices.
- Update reference applications and packaged examples.
- Cut only with zero hidden Deferred claims and explicit settings/research dispositions.

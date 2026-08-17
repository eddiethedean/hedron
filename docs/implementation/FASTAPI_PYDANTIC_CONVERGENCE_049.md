# FastAPI/Pydantic convergence implementation plan (phase 0.49)

**Status:** Planned; Stage 0 requirements<br>
**Decision/RFC:** D-081 / [RFC-0076](../rfcs/RFC-0076-FASTAPI-PYDANTIC-CONVERGENCE.md)<br>
**Target:** Hedron `v0.49.0`<br>
**Required predecessor:** Verified `v0.48.0`

## Architecture

The implementation has five one-way layers:

1. Portable lifetime, binding, schema, scope, response, and disposition values in `hedron-core`.
2. Pydantic compilation in `hedron`, producing sanitized plans without executing handlers.
3. FastAPI route/dependency/OpenAPI projection using documented stable APIs.
4. Flask/Django and package projection over the same portable plans.
5. Explorer/CLI/scenario/conformance evidence that never becomes runtime authority.

## Work packages

### M1 — Baseline and inventories

- Lock FastAPI/Pydantic/Starlette/Python matrices and all stable versus alpha/experimental APIs.
- Capture current route signatures, OpenAPI, TypeSchema, errors, lifecycle, adapter, startup, and
  request benchmarks.
- Produce exact model-shape, transport, settings-source, and response inventories.

### M2 — Dependency lifetimes

- Define `DependencyLifetime` and `DependencyPlan` in portable core.
- Compile FastAPI handler/response scopes and validate dependency graph cleanup order.
- Add streaming/SSE/download/background capture diagnostics and fixtures.
- Preserve user-authored FastAPI dependencies and provide explicit no-inference fallback.

### M3 — Binding strategy

- Define `BoundaryBindingPlan` and deterministic native eligibility rules.
- Implement query/header/cookie/form native-model compilation.
- Retain expanded path/query/file/multipart and portable-adapter paths.
- Prove model/error/OpenAPI/CSRF/alias/extra parity across strategies and adapters.

### M4 — Dual TypeSchema

- Introduce TypeSchema v2 with validation/serialization projections and fingerprints.
- Implement a closed Hedron JSON-schema generator and sanitizer.
- Classify shared/read-only/write-only/computed/secret/unsupported fields.
- Add v1 read/upgrade, static tooling, catalog/manifest/MCP/Gradio consumers, and rollback.

### M5 — Tagged unions and adapters

- Inventory public wire unions and migrate a bounded representative set.
- Cache TypeAdapters per type/version boundary and measure direct JSON validation.
- Preserve duplicate-key, size/depth/count, redaction, and canonical encoding policy.
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
- Lock strict JSON content type under security profiles and test custom transports.
- Add adversarial scope-confusion, content-type, schema leak, and callback overclaim cases.

### M8 — Settings evaluation

- Spike pydantic-settings in Workbench/Posit packages only.
- Compare source precedence/provenance, unknowns, secrets, digests, import I/O, paths, and rollback.
- Adopt per package only if all compatibility and operations requirements pass; otherwise record
  `retain-custom-loader`.

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


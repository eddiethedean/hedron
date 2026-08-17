# Hedron `v0.49` FastAPI/Pydantic convergence acceptance

**Status:** Published in-tree `v0.49.0` (tag/PyPI deferred). Does **not** close `SR-021`.<br>
**Planning baseline:** Published in-tree `v0.48.0`<br>
**Required predecessor/cut baseline:** Verified `v0.48.0`<br>
**Target:** Hedron `v0.49.0`<br>
**Decision/RFC:** D-081 / D-084 / [RFC-0076](../rfcs/RFC-0076-FASTAPI-PYDANTIC-CONVERGENCE.md)<br>
**Tracking:** [#380](https://github.com/eddiethedean/hedron/issues/380)

D-084 named shipped 0.48 seams and rebased the planning baseline. Stage 1 compiled
those plans onto FastAPI as in-tree `v0.49.0`. Tag/PyPI remain deferred.

## Release contract

- Stable upstream features replace manual machinery only when portable behavior and rollback pass.
- Dependency lifetimes are explicit and safe for ordinary and streaming responses.
- Native and expanded binding strategies are deterministic, inspectable, and equivalent.
- TypeSchema separates sanitized input and output projections.
- New wire unions are tagged; router/OpenAPI/security facts agree with runtime declarations.
- Settings and experimental research receive honest dispositions, not implicit availability.

## Exact gate matrix

| Gate | Verified means |
|---|---|
| `LIFETIME-049` | Handler/response lifetime values, FastAPI compilation, dependency graph, streaming/SSE/download/background cleanup, diagnostics, and adapter dispositions pass. |
| `BINDING-049` | Native query/header/cookie/form eligibility, expanded path/file fallback, aliases/extras/errors/CSRF/OpenAPI/model equivalence, and override pass. |
| `SCHEMA-049` | Sanitized validation/serialization projections, shared/read/write/computed/secret disposition, fingerprints, v1 upgrade, consumers, and hostile schema failures pass. |
| `UNION-049` | Stable discriminators, representative event/outcome/update/manifest/transport migrations, unknown variants, OpenAPI, bounds, and cross-runtime fixtures pass. |
| `ROUTER-049` | Preserved nested route identity/provenance, pre-seal late registration, duplicate/seal failures, plugin/package composition, and no alpha hook reliance pass. |
| `OPENAPI-049` | Typed statuses/media/headers/SSE/downloads/callbacks/webhooks/security/operation ids/input-output schemas and generated-client fixtures pass. |
| `SECURITY-049` | Strict content type, binding parity, scopes non-authority, schema/secret/subclass safety, callback honesty, transport bounds, and adversarial review pass. |
| `ADAPTER-VALIDATION-049` | Cached TypeAdapter candidates, direct JSON path, duplicate keys, bounds, errors, canonicalization, redaction, benchmarks, and rollback pass. FailFast is not this gate. |
| `SETTINGS-049` | Each deployment package records adopt or retain-custom-loader after precedence/provenance/unknown/secret/digest/I-O/path/compatibility evidence. |
| `RESEARCH-049` | Partial validation, unset/PATCH, and FailFast spikes record explicit experimental/defer/exclude dispositions with no Supported leakage. |
| `A11Y-049` | Schema/form labels, required/read/write/computed state, error summaries/paths/focus, binding parity, and scoped AT honesty pass. |
| `PERF-049` | Startup/schema/OpenAPI/route, binding, validation/serialization, adapter, streaming resource hold, error, memory, and no-opt-in budgets pass. |
| `COMPAT-049` | Direct FastAPI, structural/expanded binding, HTML, Flask/Django, package consumers, v1 schemas, upstream skew, deprecation, rollback, and exclusions pass. |
| `DOCS-049` | Authoring, lifetime, binding, schemas, unions, OpenAPI/security, settings, research, operations, migration, troubleshooting, and limitations are complete. |
| `REGRESS-049` | Full Supported suite passes with no phase-owned blocker/high issue and no hidden Deferred claim. |
| `PKG-049` | Clean wheel/sdist, dependency bounds, Python/upstream/adapter matrices, SBOM/provenance, versions, and release rehearsal pass. |

## Stage 0 entry

- [x] D-081 and RFC-0076 define adoption, portability, authority, and exclusion boundaries.
- [x] API, implementation, inventory, upgrade, gate, roadmap, decision, and traceability artifacts exist.
- [x] Stage 0 changes documentation/contracts only; no 0.49 runtime/version claim (completed before Stage 1).
- [x] D-084 rebases the living/planning baseline to Published in-tree `v0.48.0` and names shipped seams.
- [x] Tracking issue [#380](https://github.com/eddiethedean/hedron/issues/380) is bound.
- [x] In-tree Verified 0.48 is enough predecessor evidence; do not wait on PyPI/Git `#373` assets.
- [x] Stage 1 locked numeric limits, exact union symbols, adapter benchmarks, and settings-spike evidence.

## Cut result

In-tree `v0.49.0` is Published. Git tag / PyPI remain deferred. `SETTINGS-049` recorded
**retain-custom-loader**. `RESEARCH-049` stays Experimental. `SR-021` stays open.

Locks: [fastapi-lifetime-049.toml](fastapi-lifetime-049.toml) ·
[fastapi-binding-049.toml](fastapi-binding-049.toml) ·
[typeschema-v2-049.toml](typeschema-v2-049.toml) ·
[fastapi-unions-openapi-049.toml](fastapi-unions-openapi-049.toml) ·
[fastapi-settings-research-049.toml](fastapi-settings-research-049.toml).

## Cut rule

Do not cut `v0.49.0` until every non-disposition gate in
[`release-gate-0.49.toml`](release-gate-0.49.toml) is Verified. `SETTINGS-049` and `RESEARCH-049`
must contain explicit per-candidate dispositions; deferred or excluded candidates cannot appear in
the Supported inventory.

# Hedron `v0.49` FastAPI/Pydantic convergence acceptance

**Status:** Planned; Stage 0 requirements packet complete<br>
**Planning baseline:** Published in-tree `v0.46.0`<br>
**Required predecessor/cut baseline:** Verified `v0.48.0`<br>
**Target:** Hedron `v0.49.0`<br>
**Decision/RFC:** D-081 / [RFC-0076](../rfcs/RFC-0076-FASTAPI-PYDANTIC-CONVERGENCE.md)

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
| `ADAPTER-VALIDATION-049` | Cached TypeAdapter candidates, direct JSON path, duplicate keys, bounds, errors, canonicalization, redaction, benchmarks, and rollback pass. |
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
- [x] Stage 0 changes documentation/contracts only; no 0.49 runtime/version claim.
- [ ] Verified 0.48 and a tracking issue are bound before Stage 1.
- [ ] Stage 1 locks binding eligibility, schema subset, migration inventory, and performance budgets.

## Cut rule

Do not cut `v0.49.0` until every non-disposition gate in
[`release-gate-0.49.toml`](release-gate-0.49.toml) is Verified. `SETTINGS-049` and `RESEARCH-049`
must contain explicit per-candidate dispositions; deferred or excluded candidates cannot appear in
the Supported inventory.


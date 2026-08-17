# Hedron `v0.46` package-native typed workflow acceptance

**Status:** Planned; Stage 0 requirements packet complete; contract-refined by D-079<br>
**Planning baseline:** Published in-tree `v0.45.0` (D-079; original Stage 0 baseline was Published `v0.42.0`)<br>
**Required predecessor/cut baseline:** Verified in-tree `v0.45.0`<br>
**Target:** `v0.46.0`<br>
**Decision/RFC:** D-075, refined by D-079 / [RFC-0073](../rfcs/RFC-0073-PACKAGE-NATIVE-WORKFLOWS.md)

Phase 0.46 uses the 0.45 ecosystem contract to deliver opt-in package features: atomic feature
bundles, bounded data workspaces, explicit chart/data links, schema-aware elements, explicit MCP/
Gradio workflows, and catalog-backed workbench/scenario experiences. Every feature compiles to the
ordinary 0.43–0.45 stack and owns no parallel runtime.

D-079 rebases planning onto shipped 0.43 `BaseHandleDescriptor` / `descriptor_fingerprint` /
`Hedron.include_component`, 0.44 `hedron.type`, and 0.45 `InteractionCatalog` /
`PackageProjection` / `Hedron.interactions` seams, plus `DataEditorSource` and first-party
`hedron-chart` kinds. It does not authorize Stage 1.

Implementation requirements:
[PACKAGE_NATIVE_WORKFLOWS_046](../implementation/PACKAGE_NATIVE_WORKFLOWS_046.md). Public contract:
[PACKAGE_WORKFLOWS](../api/PACKAGE_WORKFLOWS.md). Capability/feature inventory:
[`package-workflow-capability-inventory-046.toml`](package-workflow-capability-inventory-046.toml).
Bundle/workspace/chart locks:
[`feature-bundle-046.toml`](feature-bundle-046.toml),
[`data-workspace-046.toml`](data-workspace-046.toml),
[`chart-interaction-046.toml`](chart-interaction-046.toml).
Evidence index: [`release-gate-0.46.toml`](release-gate-0.46.toml). Upgrade fixtures:
[upgrade-fixtures-046](upgrade-fixtures-046.md).

## Release contract

- `FeatureBundle` is an atomic registration/composition unit for ordinary handles, components,
  scenarios, requirements, and projections; it is not an executor.
- `DataWorkspace` requires explicit models, already-authorized source/factory, and mutation policy;
  its initial inventory is list/detail/create/edit with full override/eject paths.
- `ChartInteraction` maps a closed typed event inventory to explicit commands/effects with cycle,
  fan-out, event, payload, target, and accessibility bounds.
- Supported elements enhance the closed control inventory while native forms remain canonical.
- MCP exposure and Gradio remote workflows remain separate explicit policies with live authz,
  confirmation/egress/files/jobs/bounds/audit.
- Explorer/Jinja/extras/notebook/sim/scenario/conformance experiences consume 0.45 catalog facts and
  generate reviewable code/tests, never an opaque production workflow.
- Existing applications/direct package APIs remain unchanged without opt-in and rollback/ejection
  leaves no orphan artifacts.

## Exact gate matrix

| Gate | Verified means |
|---|---|
| `BUNDLE-046` | Immutable bundles, atomic inclusion, conflicts, dependencies, capability checks, deterministic config, plugin isolation, cleanup, eject, and rollback pass. |
| `DATAFLOW-046` | Explicit sources/policies, list/detail/create/edit, query/identity, forms/outcomes, authz, transactions/conflicts/optimism, overrides, bounds, hosts, and direct APIs pass. |
| `VISUAL-046` | `select`/`inspect`/`focus`/`reset` plus export-as-command; `legend_filter`/`brush`/`drill_intent` Experimental until host+a11y; explicit event/command/effect graph, cycle/fan-out/rate/payload/state/authz/fallback/adapter/race behavior pass. |
| `ELEMENT-046` | Closed control map, native encoding/semantics, typed events, async command states, secrets, failed/no-JS/CSP fallback, swap lifecycle, and ABI compatibility pass. |
| `REMOTE-046` | Explicit MCP/Gradio policies, schemas, authz/confirmation, outputs/effects, egress/files/jobs/progress/cancellation/audit, denial, and rollback pass. |
| `WORKBENCH-046` | Explorer/Jinja/extras/notebook/sim/CLI inspection, safe execution, reviewable generation, static boundaries, accessibility, cleanup, and performance pass. |
| `SCENARIO-046` | AppScenario, generated reviewable tests, conformance/sample-kit/Node/Java, fuzz, real-service separation, package data, and offline evidence pass. |
| `ADAPTER-046` | FastAPI/Flask/Django public host behavior, semantic/host fingerprints, Posit/Workbench mounts, deployment, clean imports, and limitations pass. |
| `SECURITY-046` | Bundle/source/event/remote/file/generated-code threat model, authority preservation, redaction, allowlists, bounds, destructive deny, tool policies, and review pass. |
| `A11Y-046` | Data/chart/element/workbench semantics, labels/errors/focus, keyboard/tabular alternatives, native fallback, responsive visual modes, and evidence honesty pass. |
| `BROWSER-046` | Chromium/Firefox/WebKit integrated native/HTMX/enhanced/no-JS, rapid update, race, cancellation, disconnect, failure, and cleanup workflows pass. |
| `COMPAT-046` | Unchanged 0.42–0.45, direct package APIs, ordinary compiled semantics, incremental adopt/eject, clean optionality, skew/absence/outage/failure/rollback pass. |
| `PERF-046` | Registration, explicit-path delta, query/render/mutation, chart event, element upgrade, remote/tooling, allocation/payload/concurrency/memory and amplification budgets pass. |
| `DOCS-046` | API/package/recipe/customize/eject/security/a11y/testing/remote/deployment/migration/troubleshooting/limitation docs are complete. |
| `REGRESS-046` | Full Supported suite passes with zero phase-owned unresolved blocker/high regression. |
| `PKG-046` | Feature inventory, clean fleet packages, version/dependency/stability/changelog/release rehearsal and zero-Deferred verification pass. |

## Stage 0 entry

- [x] D-075 and RFC-0073 define the accepted feature and authority boundaries.
- [x] D-079 rebases planning onto Published in-tree `v0.45.0` and locks
  bundle/workspace/chart inventories.
- [x] API, implementation, inventory, gate, acceptance, upgrade, roadmap, index, status, and
  traceability artifacts exist.
- [x] Published/living baseline remains `v0.45.0`; no package/runtime version changed.
- [x] Verified `v0.45.0` is the Stage 1 prerequisite and cut baseline.
- [x] Initial package-feature inventory and exclusions are machine-readable.
- [ ] A tracking issue is created and bound to every 0.46 gate.
- [ ] Every predecessor-owned gate is Verified before runtime work begins.
- [ ] Stage 1 records equivalent explicit 0.45 package/handle performance and behavior baselines.

## Feature bundle acceptance

- [ ] Bundle inclusion validates complete changes and registers all-or-nothing before seal.
- [ ] Id/route/component/asset/projection conflicts, dependency cycles/depth/skew, stale
  fingerprints, and missing required capabilities fail without partial artifacts.
- [ ] Providers use public APIs and bundle execution always resolves to ordinary handles/routes/
  components/scenarios/catalog entries.
- [ ] Disable/uninstall/eject/rollback removes every owned artifact and preserves explicit APIs.
- [ ] Sample-kit proves third-party namespace/dependency/capability/Explorer/scenario behavior.

## Data and visualization acceptance

- [ ] DataWorkspace refuses absent source/policy and never discovers ORM/models/tenants/routes.
- [ ] List/detail/create/edit cover supported query/model/form/outcome shapes and require overrides
  for ambiguity or unsupported fields.
- [ ] Every read/mutation repeats authz/source scoping; transaction/idempotency/retry/audit/conflict
  policy remains explicit.
- [ ] Delete/bulk/nested relations are absent by default and high-risk optimism fails closed.
- [ ] Chart selection/filter/drill-down/export events validate typed untrusted input and execute
  registered commands with explicit effects.
- [ ] Link graph cycles/fan-out/rate/payload/selection/refresh costs are bounded and races/stale
  responses/cancellation are deterministic.
- [ ] Keyboard/tabular/no-JS chart alternatives and data native forms provide equivalent essential
  information/actions.

## Element and remote acceptance

- [ ] Every enhanced control maps from an inventoried supported schema or remains native/requires
  override; encoding, CSRF, labels/errors/focus/retention/no-JS parity passes.
- [ ] Typed element events target only registered commands; async states retain ordinary fallback
  and server authority under failed upgrade/disconnect/replacement.
- [ ] MCP exposure is separate and explicit, repeats authz/confirmation/bounds/audit, and grants no
  DOM or undeclared follow-up authority.
- [ ] Gradio workflows require allowlisted adapter/endpoint/local models/outcome map/egress-file-job
  policy and treat remote metadata/results as untrusted.
- [ ] Remote denial/drift/outage/files/progress/cancel/timeout/partial/multi-worker/rollback cases
  preserve local workflows.

## Workbench, scenarios, and host acceptance

- [ ] Explorer consumes catalog/bundle projections and shows composition, capabilities, outcomes,
  effects, cost, security/a11y, adapters, and provenance without reinspection.
- [ ] Generated Python/tests are deterministic, reviewable, safe-path/no-overwrite, and include
  explicit policies rather than captured state/secrets.
- [ ] Jinja/extras/notebook/sim retain explicit trust, localhost/offline, sandbox, and unsupported
  behavior boundaries.
- [ ] Every first-party feature ships synthetic `AppScenario` and portable conformance coverage.
- [ ] FastAPI/Flask/Django and Posit/Workbench deployments preserve public host authority, mounts,
  assets, catalog, limitations, restart/multi-worker/rollback, and clean imports.

## Security, accessibility, performance, and compatibility acceptance

- [ ] No model/type/name/catalog/bundle infers authz/tenancy/transaction/idempotency/retry/
  destructive safety/business validation/exposure.
- [ ] Sensitive source/model/file/credential/remote data is absent from ids/events/forms/outcomes/
  catalog/tools/scenarios/logs/traces/errors and hostile/generated paths are escaped/bounded.
- [ ] Browser and automated accessibility matrices cover integrated workflows and preserve scoped
  claim honesty without closing `SR-021`.
- [ ] Performance compares every abstraction with equivalent explicit 0.45 paths and detects N+1,
  fan-out, retry, query, memory, or browser-resource amplification.
- [ ] Existing 0.42–0.45 apps/direct APIs, package absence/skew, remote outage, failed inclusion,
  rolling deploy, eject, and full 0.45 rollback pass.
- [ ] Security review records zero unresolved critical/high findings.
- [ ] Every row in `release-gate-0.46.toml` is Verified with retained evidence and none is Deferred.

## Verification entry points

```bash
python scripts/check_bundles_046.py
python scripts/check_data_workspaces_046.py
python scripts/check_visual_workflows_046.py
python scripts/check_element_workflows_046.py
python scripts/check_remote_workflows_046.py
python scripts/check_security_046.py
python scripts/check_compat_046.py
python scripts/verify_pkg_46.py
python scripts/check_release_gate.py 0.46.0 --execute-verified
```

`v0.46.0` may be cut only from Verified `v0.45.0` when every 0.46 row is Verified with zero
Deferred.


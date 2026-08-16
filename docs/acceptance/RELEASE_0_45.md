# Hedron `v0.45` typed interaction ecosystem acceptance

**Status:** **Published** in-tree as `v0.45.0` (tag/PyPI deferred; D-074 / D-077)<br>
**Planning baseline:** Published in-tree `v0.44.0`<br>
**Required predecessor/cut baseline:** Verified in-tree `v0.44.0`<br>
**Target:** `v0.45.0` (in-tree; tag/PyPI deferred)<br>
**Decision/RFC:** D-074, refined by D-077 / [RFC-0072](../rfcs/RFC-0072-TYPED-INTERACTION-ECOSYSTEM.md)
**Tracking:** [#328](https://github.com/eddiethedean/hedron/issues/328) remains open until later tag/PyPI assets exist.

Phase 0.45 makes the 0.43/0.44 interaction contract consumable across the whole package fleet
through one sealed catalog, one redacted manifest, and one bounded package-projection protocol.
It adds no third runtime/schema authority and cannot begin implementation until 0.44 is Verified.
D-077 rebases planning onto shipped 0.43 `BaseHandleDescriptor` / `descriptor_fingerprint` /
`BindingAdapter` seams and 0.44 `TypeSchema` under `hedron.type` with `OutcomeMap(case(...), ...)`.
The refine does not authorize Stage 1.

Implementation requirements:
[TYPED_INTERACTION_ECOSYSTEM_045](../implementation/TYPED_INTERACTION_ECOSYSTEM_045.md). Public
contract: [INTERACTION_CATALOG](../api/INTERACTION_CATALOG.md). Capability/disposition inventory:
[`ecosystem-capability-inventory-045.toml`](ecosystem-capability-inventory-045.toml). Entry lock:
[`catalog-entry-045.toml`](catalog-entry-045.toml). Manifest lock:
[`manifest-format-045.toml`](manifest-format-045.toml). Host lock:
[`host-portable-facts-045.toml`](host-portable-facts-045.toml). Evidence index:
[`release-gate-0.45.toml`](release-gate-0.45.toml). Upgrade fixtures:
[upgrade-fixtures-045](upgrade-fixtures-045.md).

## Release contract

- `InteractionCatalog` indexes authoritative base descriptors and optional matching type extensions
  without reconstructing or executing them.
- `InteractionManifest` is deterministic, versioned, redacted, bounded, atomically emitted, and
  validated against the live sealed catalog.
- `PackageProjection` is namespaced, capability-labeled, fingerprint-bound metadata with no route,
  policy, form, effect, outcome, execution, or exposure authority.
- Trusted dynamic and no-import static modes are distinct and report provenance/unknown facts.
- FastAPI, Flask, and Django agree on portable facts and expose machine-readable host limitations.
- Explorer, CLI, OpenAPI, Jinja, scenarios, conformance, sim, notebook, deployment, and package
  consumers use the same contract.
- MCP and Gradio projections remain separate, explicit, deny-by-default, bounded, and authorized.
- Every package/runtime has an owned `native_consumer`, `projection_adapter`,
  `compatibility_only`, or `not_applicable` disposition.
- 0.45 does not implement the package-native workflow features reserved for 0.46.

## Exact gate matrix

| Gate | Verified means |
|---|---|
| `CATALOG-045` | Immutable compiler/entries, authority references, sealing, deterministic ordering, app ownership, concurrency, unmodeled behavior, and no-execution pass. |
| `MANIFEST-045` | Format/schema, canonical bytes, redaction profiles, trusted/static modes, atomic I/O, startup validation, compatibility, and bounds pass. |
| `PROJECTION-045` | Provider protocol, namespaces, fingerprints, capability labels, version skew, cache invalidation, optionality, third-party isolation, and rollback pass. |
| `HOST-045` | FastAPI/Flask/Django portable equivalence, public host APIs, declared exceptions, mounts, native/HTMX/no-JS, and clean imports pass. |
| `AUTHOR-045` | Jinja registered-handle helpers, plugins, sample-kit, scaffolds, diagnostics, no manifest execution, and uninstall pass. |
| `SURFACE-045` | Data/chart/element/extras current-surface projections, coexistence, limitations, direct APIs, and absence pass without 0.46 features. |
| `REMOTE-045` | MCP/Gradio explicit exposure/egress/authz, untrusted remote schemas, files/jobs/cancellation/bounds/audit, denial, and rollback pass. |
| `TOOLING-045` | Explorer, CLI, build, OpenAPI, AppScenario, diagnostics, static no-exec, drift, large-catalog, and redaction pass. |
| `PORTABLE-045` | Conformance/sim/notebook/sample-kit/Node/Java fixtures, offline/localhost limits, artifact compatibility, clean wheels, and provenance pass. |
| `DEPLOY-045` | Posit/Workbench/Connect mounts, external URLs, manifests, restarts, multi-worker, read-only filesystems, version skew, and rollback pass. |
| `SECURITY-045` | Threat model, sensitive-data absence, hostile JSON/projections, provider trust, cross-app/stale/downgrade/path/TOCTOU cases, tool access, and review pass. |
| `A11Y-045` | Native form semantics, graph/table keyboard use, focus/errors/fallback, capability-claim honesty, and automated accessibility pass. |
| `BROWSER-045` | Chromium/Firefox/WebKit package/tooling projection, native/enhanced, stale/missing provider, swap, cancellation, and cleanup workflows pass. |
| `COMPAT-045` | Unchanged 0.42–0.44, frozen predecessor authority, whole-fleet dispositions, direct APIs, skew, provider removal, deployment rollback, and 0.44 rollback pass. |
| `PERF-045` | Compile/seal/lookup/manifest/projection/tool/startup/allocation/payload/concurrency/memory budgets and unused-path neutrality pass. |
| `DOCS-045` | API, app, package-author, host, tooling, format, security, deployment, migration, troubleshooting, and 0.46 boundary docs are complete. |
| `REGRESS-045` | Full Supported suite passes with zero phase-owned unresolved blocker/high regression. |
| `PKG-045` | Whole-fleet package/disposition/version/dependency/inventory/release rehearsal and zero-Deferred verification pass. |

Reserved command names in the manifest are not evidence until their scripts and retained artifacts
exist.

## Stage 0 entry

- [x] D-074 and RFC-0072 define the accepted phase and authority hierarchy.
- [x] D-077 rebases planning onto Published in-tree `v0.44.0` and locks
  catalog-entry/manifest/host inventories. No runtime or version bump.
- [x] API, implementation, inventory, gate, acceptance, upgrade, roadmap, index, status, and
  traceability artifacts exist.
- [x] Published/living baseline is `v0.44.0`; no package/runtime version changed by this refine.
- [x] Verified in-tree `v0.44.0` is the Stage 1 prerequisite and cut baseline. Stage 1 does not
  wait on `#318`/`#311` PyPI/Git assets. This refine does not authorize Stage 1.
- [x] Phase 0.46 feature bundles/workflows are explicitly excluded from 0.45.
- [x] Every 0.43/0.44-owned gate is Verified in-tree.
- [x] A tracking issue is created and bound to every 0.45 gate:
  [#328](https://github.com/eddiethedean/hedron/issues/328).
- [x] Stage 1 records descriptor/type/route/form/effect/outcome/package baselines.

## Catalog and manifest acceptance

- [x] Every registered 0.43 view/command appears exactly once with correct descriptor/type
  versions/fingerprints, effect label, provenance, limitations, and app ownership.
- [x] Unmodeled handles remain coarse/dynamic and absent optional type/projection data is honest.
- [x] Registration conflicts and stale/cross-app artifacts fail atomically before publication.
- [x] Catalog reads never execute handlers/dependencies/providers or perform I/O.
- [x] Equivalent registries produce deterministic catalog and canonical manifest fingerprints.
- [x] Production/development/conformance profiles pass secret/source/default/example/request-value
  redaction goldens.
- [x] Trusted build and static/no-execution modes have distinct provenance and behavior.
- [x] Production-required manifest mismatch fails before serving and rollback is atomic.
- [x] Unknown optional and incompatible required versions follow documented compatibility rules.

## Projection and package acceptance

- [x] Projection namespaces/versions/provider/config/fingerprints/capabilities/limitations/bounds are
  validated and unknown optional projections cannot change base behavior.
- [x] Provider disable/uninstall removes only its projection and leaks no registry/cache/resource.
- [x] Third-party sample provider receives no privileged registry/app/dependency/secret access.
- [x] Every package/runtime row in the inventory has an owner, exact compatibility range,
  capability/limitation evidence, clean import, and rollback path.
- [x] Data/chart/element/extras projections describe current surfaces only; no feature bundle,
  DataWorkspace, chart-link, or remote-workflow factory is present.
- [x] Independently versioned satellites and maturity/readiness labels remain honest.

## Consumer acceptance

- [x] FastAPI/Flask/Django agree on portable semantic goldens and expose host-specific limitations.
- [x] Jinja resolves only registered handles/logical ids and retains reversal/CSRF/validation/
  escaping/fallback without annotation or manifest execution.
- [x] Explorer/CLI/OpenAPI/scenarios use the catalog, expose static/trusted provenance, and pass
  stale/large/unsupported/redaction cases.
- [x] Conformance/sim/notebook/sample-kit/Node/Java consumers pass their declared portable subset
  and refuse unsupported server/remote/browser behavior.
- [x] Posit/Workbench/Connect preserve mount-aware diagnostics and manifest validation without
  moving Hedron logic into `fastapi-workbench`.
- [x] MCP/Gradio create no operation from catalog presence; explicit adapters repeat live authz/
  egress/bounds/audit and fail closed.

## Security, accessibility, and performance acceptance

- [x] Catalog/manifest/projection ids and fingerprints are never treated as capabilities.
- [x] Hostile JSON, provider metadata, paths, symlinks, partial writes, downgrade, namespace,
  cross-app, stale, injection, and TOCTOU corpora pass.
- [x] Explorer/CLI/notebook/deployment retain authentication/origin/CSRF/rate/token/production
  controls and structured redacted audit.
- [x] Native form/no-JS semantics and Explorer graph/table keyboard/focus/error/visual-mode behavior
  pass three-engine browser evidence without a new human-AT claim.
- [x] Performance evidence separates compile/build/tooling cost from request-path cost and proves
  no material unused-path regression or new required browser asset.
- [x] Security review records zero unresolved critical/high findings.

## Compatibility and release acceptance

- [x] Published 0.42, Published 0.43 unmodeled-handle, and Published 0.44 modeled fixtures pass
  unchanged.
- [x] Mixed versions, rolling deploy, unknown projection, missing provider/package, manifest
  rollback, provider uninstall, and full 0.44 rollback pass.
- [x] Wheel/sdist/source/offline imports preserve package dependency direction and optionality.
- [x] API/stability/package/disposition/format documentation and changelogs agree.
- [x] Every row in `release-gate-0.45.toml` is Verified with retained evidence and none is Deferred.

## Verification entry points

```bash
python scripts/check_catalog_045.py
python scripts/check_manifest_045.py
python scripts/check_projections_045.py
python scripts/check_hosts_045.py
python scripts/check_security_045.py
python scripts/check_compat_045.py
python scripts/verify_pkg_45.py
python scripts/check_release_gate.py 0.45.0 --execute-verified
```

`v0.45.0` is cut in-tree from Verified `v0.44.0` with every 0.45 row Verified and zero
Deferred. Git tag, GitHub Release, and PyPI remain deferred; tracking [#328] stays open.
`verify_pkg_45.py` (no `--allow-planned`) is the living-train cut checker.


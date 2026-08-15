# Hedron `v0.45` typed interaction ecosystem acceptance

**Status:** Planned; Stage 0 requirements packet complete<br>
**Planning baseline:** Published `v0.42.0`<br>
**Required predecessor/cut baseline:** Verified `v0.44.0`<br>
**Target:** `v0.45.0`<br>
**Decision/RFC:** D-074 / [RFC-0072](../rfcs/RFC-0072-TYPED-INTERACTION-ECOSYSTEM.md)

Phase 0.45 makes the 0.43/0.44 interaction contract consumable across the whole package fleet
through one sealed catalog, one redacted manifest, and one bounded package-projection protocol.
It adds no third runtime/schema authority and cannot begin implementation until 0.44 is Verified.

Implementation requirements:
[TYPED_INTERACTION_ECOSYSTEM_045](../implementation/TYPED_INTERACTION_ECOSYSTEM_045.md). Public
contract: [INTERACTION_CATALOG](../api/INTERACTION_CATALOG.md). Capability/disposition inventory:
[`ecosystem-capability-inventory-045.toml`](ecosystem-capability-inventory-045.toml). Evidence index:
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
- [x] API, implementation, inventory, gate, acceptance, upgrade, roadmap, index, status, and
  traceability artifacts exist.
- [x] Published/living baseline remains `v0.42.0`; no package/runtime version changed.
- [x] Verified `v0.44.0` is the Stage 1 prerequisite and cut baseline.
- [x] Phase 0.46 feature bundles/workflows are explicitly excluded from 0.45.
- [ ] A tracking issue is created and bound to every 0.45 gate.
- [ ] Every 0.43/0.44-owned gate is Verified before runtime work begins.
- [ ] Stage 1 records descriptor/type/route/form/effect/outcome/package baselines.

## Catalog and manifest acceptance

- [ ] Every registered 0.43 view/command appears exactly once with correct descriptor/type
  versions/fingerprints, effect label, provenance, limitations, and app ownership.
- [ ] Unmodeled handles remain coarse/dynamic and absent optional type/projection data is honest.
- [ ] Registration conflicts and stale/cross-app artifacts fail atomically before publication.
- [ ] Catalog reads never execute handlers/dependencies/providers or perform I/O.
- [ ] Equivalent registries produce deterministic catalog and canonical manifest fingerprints.
- [ ] Production/development/conformance profiles pass secret/source/default/example/request-value
  redaction goldens.
- [ ] Trusted build and static/no-execution modes have distinct provenance and behavior.
- [ ] Production-required manifest mismatch fails before serving and rollback is atomic.
- [ ] Unknown optional and incompatible required versions follow documented compatibility rules.

## Projection and package acceptance

- [ ] Projection namespaces/versions/provider/config/fingerprints/capabilities/limitations/bounds are
  validated and unknown optional projections cannot change base behavior.
- [ ] Provider disable/uninstall removes only its projection and leaks no registry/cache/resource.
- [ ] Third-party sample provider receives no privileged registry/app/dependency/secret access.
- [ ] Every package/runtime row in the inventory has an owner, exact compatibility range,
  capability/limitation evidence, clean import, and rollback path.
- [ ] Data/chart/element/extras projections describe current surfaces only; no feature bundle,
  DataWorkspace, chart-link, or remote-workflow factory is present.
- [ ] Independently versioned satellites and maturity/readiness labels remain honest.

## Consumer acceptance

- [ ] FastAPI/Flask/Django agree on portable semantic goldens and expose host-specific limitations.
- [ ] Jinja resolves only registered handles/logical ids and retains reversal/CSRF/validation/
  escaping/fallback without annotation or manifest execution.
- [ ] Explorer/CLI/OpenAPI/scenarios use the catalog, expose static/trusted provenance, and pass
  stale/large/unsupported/redaction cases.
- [ ] Conformance/sim/notebook/sample-kit/Node/Java consumers pass their declared portable subset
  and refuse unsupported server/remote/browser behavior.
- [ ] Posit/Workbench/Connect preserve mount-aware diagnostics and manifest validation without
  moving Hedron logic into `fastapi-workbench`.
- [ ] MCP/Gradio create no operation from catalog presence; explicit adapters repeat live authz/
  egress/bounds/audit and fail closed.

## Security, accessibility, and performance acceptance

- [ ] Catalog/manifest/projection ids and fingerprints are never treated as capabilities.
- [ ] Hostile JSON, provider metadata, paths, symlinks, partial writes, downgrade, namespace,
  cross-app, stale, injection, and TOCTOU corpora pass.
- [ ] Explorer/CLI/notebook/deployment retain authentication/origin/CSRF/rate/token/production
  controls and structured redacted audit.
- [ ] Native form/no-JS semantics and Explorer graph/table keyboard/focus/error/visual-mode behavior
  pass three-engine browser evidence without a new human-AT claim.
- [ ] Performance evidence separates compile/build/tooling cost from request-path cost and proves
  no material unused-path regression or new required browser asset.
- [ ] Security review records zero unresolved critical/high findings.

## Compatibility and release acceptance

- [ ] Published 0.42 and future Verified 0.43/0.44 fixtures pass unchanged.
- [ ] Mixed versions, rolling deploy, unknown projection, missing provider/package, manifest
  rollback, provider uninstall, and full 0.44 rollback pass.
- [ ] Wheel/sdist/source/offline imports preserve package dependency direction and optionality.
- [ ] API/stability/package/disposition/format documentation and changelogs agree.
- [ ] Every row in `release-gate-0.45.toml` is Verified with retained evidence and none is Deferred.

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

`v0.45.0` may be cut only from Verified `v0.44.0` when every 0.45 row is Verified with zero
Deferred.


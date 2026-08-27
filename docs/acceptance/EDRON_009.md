# Edron 0.9 acceptance

**Status:** Implemented and verified in-tree; publication pending

**Package target:** `edron==0.9.1` · Hedron `0.67.0` through `1.x` (`>=0.67.0,<2.0`)

**Evidence lock:** clean environments must resolve `hedron==0.67.0`, with coordinated
`hedron-core==0.67.0` and `hedron-data==0.67.0` when those capabilities are exercised. The accepted
Edron source and public contract also pass the forward-compatibility matrix on the Hedron `1.0.0`
release candidate. The widened requirement is published as the new immutable `0.9.1` patch.

Phase 0.9 consolidates the Edron 0.1–0.8 surface while consuming the native Hedron 0.67 browser,
interaction, outcome, lifecycle, and component-engine contracts. It does not copy Hedron's runtime
or turn every Hedron 0.67 feature into an Edron wrapper. The Edron 0.8.0 release remains on Hedron
0.66.2 and is the required predecessor.

Public contract outline: [Edron release roadmap](../EDRON_ROADMAP.md) ·
[Hedron 0.67 implementation plan](../implementation/ALPINE_INTEGRATION_067.md) ·
[HTMX/Alpine boundary](../api/HTMX_ALPINE_BOUNDARY_1_0.md) ·
[component-engine dispositions](../implementation/COMPONENT_ENGINE_DISPOSITIONS_067_1_0.md) ·
[upgrade fixtures](upgrade-fixtures-09.md).

| Gate | Implementation evidence | State |
|---|---|---|
| `EDR-09-TRAIN` | Edron 0.9 package bounds, lockfile, artifact metadata, and clean-install evidence all resolve the Hedron 0.67.0 train | Implemented |
| `EDR-09-NATIVE` | Edron projections preserve Hedron 0.67 native application, interaction, outcome, lifecycle, asset, and component identity | Implemented |
| `EDR-09-BROWSER` | Demand-driven Alpine/CSP/lifecycle integration, feature-off behavior, fragment closure, and native/Web Component dispositions | Implemented |
| `EDR-09-CLEAN-067` | Edron runtime, generated output, examples, docs, metadata, and browser assets contain no deprecated Hedron 0.67 compatibility path | Implemented |
| `EDR-09-MATURITY` | Symbol-level public/internal inventory with reviewed stable, beta, experimental, deferred, and application-owned dispositions | Implemented |
| `EDR-09-COMPAT` | Supported Python, Edron, Hedron 0.67, adapter, browser, and host matrix plus a Hedron 1.0 forward-compatibility matrix once released, with unsupported ranges labeled | Implemented |
| `EDR-09-DEPRECATION` | Canonical replacements, structured warnings, migration fixtures, and numeric removal windows for every transitional path | Implemented |
| `EDR-09-PERF` | Reproducible import, compile, render, request, asset, diagnostic, memory, and installation budgets | Implemented |
| `EDR-09-SECURITY` | Negative corpus for CSP, SRI, proxy trust, redirects, cookies, CSRF, downloads, secrets, and diagnostic redaction | Implemented |
| `EDR-09-A11Y` | Semantic HTML, keyboard/focus, names/roles, reduced motion, contrast guidance, screen-reader, and no-JavaScript evidence | Implemented |
| `EDR-09-PLATFORM` | Clean-process, root-path, worker, restart, shutdown, adapter, and ejection behavior for every Supported host | Implemented |
| `EDR-09-DOCS` | User guide, examples, diagnostics, API exports, compatibility policy, and generated output agree with the accepted contract | Implemented |
| `EDR-09-UPGRADE` | 0.8/Hedron 0.66.2 to 0.9/Hedron 0.67.0 upgrade, future Hedron 1.0 compatibility rehearsal, rollback, warning, stale-asset, and application-owned migration fixtures | Implemented |
| `EDR-09-REGRESSION` | Predecessor Edron regression plus all Phase 0.9 native, browser, compatibility, performance, security, accessibility, and recovery suites | Implemented |

The packet records the accepted in-tree implementation. Publication and tagging remain maintainer-
controlled. Migration tooling may recognize deprecated 0.67 input, but Edron 0.9 runtime and
generated output may not use it.

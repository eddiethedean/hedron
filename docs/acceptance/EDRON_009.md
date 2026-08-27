# Edron 0.9 acceptance

**Status:** Refined candidate; implementation pending

**Package target:** `edron==0.9.0` · Hedron `0.67.0` (`>=0.67.0,<0.68`)

**Evidence lock:** clean environments must resolve `hedron==0.67.0`, with coordinated
`hedron-core==0.67.0` and `hedron-data==0.67.0` when those capabilities are exercised. The accepted
Edron source and public contract must also pass a forward-compatibility matrix on Hedron `1.0.0`
once Hedron 1.0 is released; 1.0 is not declared as a dependency before then.

Phase 0.9 consolidates the Edron 0.1–0.8 surface while consuming the native Hedron 0.67 browser,
interaction, outcome, lifecycle, and component-engine contracts. It does not copy Hedron's runtime
or turn every Hedron 0.67 feature into an Edron wrapper. The Edron 0.8.0 release remains on Hedron
0.66.2 and is the required predecessor.

Public contract outline: [Edron release roadmap](../EDRON_ROADMAP.md) ·
[Hedron 0.67 implementation plan](../implementation/ALPINE_INTEGRATION_067.md) ·
[HTMX/Alpine boundary](../api/HTMX_ALPINE_BOUNDARY_1_0.md) ·
[component-engine dispositions](../implementation/COMPONENT_ENGINE_DISPOSITIONS_067_1_0.md) ·
[upgrade fixtures](upgrade-fixtures-09.md).

| Gate | Candidate evidence required | State |
|---|---|---|
| `EDR-09-TRAIN` | Edron 0.9 package bounds, lockfile, artifact metadata, and clean-install evidence all resolve the Hedron 0.67.0 train | Planned |
| `EDR-09-NATIVE` | Edron projections preserve Hedron 0.67 native application, interaction, outcome, lifecycle, asset, and component identity | Planned |
| `EDR-09-BROWSER` | Demand-driven Alpine/CSP/lifecycle integration, feature-off behavior, fragment closure, and native/Web Component dispositions | Planned |
| `EDR-09-CLEAN-067` | Edron runtime, generated output, examples, docs, metadata, and browser assets contain no deprecated Hedron 0.67 compatibility path | Planned |
| `EDR-09-MATURITY` | Symbol-level public/internal inventory with reviewed stable, beta, experimental, deferred, and application-owned dispositions | Planned |
| `EDR-09-COMPAT` | Supported Python, Edron, Hedron 0.67, adapter, browser, and host matrix plus a Hedron 1.0 forward-compatibility matrix once released, with unsupported ranges labeled | Planned |
| `EDR-09-DEPRECATION` | Canonical replacements, structured warnings, migration fixtures, and numeric removal windows for every transitional path | Planned |
| `EDR-09-PERF` | Reproducible import, compile, render, request, asset, diagnostic, memory, and installation budgets | Planned |
| `EDR-09-SECURITY` | Negative corpus for CSP, SRI, proxy trust, redirects, cookies, CSRF, downloads, secrets, and diagnostic redaction | Planned |
| `EDR-09-A11Y` | Semantic HTML, keyboard/focus, names/roles, reduced motion, contrast guidance, screen-reader, and no-JavaScript evidence | Planned |
| `EDR-09-PLATFORM` | Clean-process, root-path, worker, restart, shutdown, adapter, and ejection behavior for every Supported host | Planned |
| `EDR-09-DOCS` | User guide, examples, diagnostics, API exports, compatibility policy, and generated output agree with the accepted contract | Planned |
| `EDR-09-UPGRADE` | 0.8/Hedron 0.66.2 to 0.9/Hedron 0.67.0 upgrade, future Hedron 1.0 compatibility rehearsal, rollback, warning, stale-asset, and application-owned migration fixtures | Planned |
| `EDR-09-REGRESSION` | Predecessor Edron regression plus all Phase 0.9 native, browser, compatibility, performance, security, accessibility, and recovery suites | Planned |

The packet is a planning lock, not an availability claim. No Edron 0.9 package metadata, public API,
stable classification, or 0.9 tag is authorized until the gates are accepted, the exact Hedron
0.67.0 evidence is retained, the future 1.0 compatibility rehearsal passes when available, and
the deprecated-feature exclusion scan is clean. Migration tooling may recognize deprecated 0.67
input, but Edron 0.9 runtime and generated output may not use it.

# Release acceptance: 0.63 interaction tooling and interoperability

**Status:** Proposed / Planned gates  
**Implementation:** [INTERACTION_TOOLING_063](../implementation/INTERACTION_TOOLING_063.md)

## Planned contract artifacts

- `interaction-capability-inventory-063.toml`
- `interaction-trace-conformance-063.toml`
- `interaction-profiler-contract-063.toml`
- `interaction-check-catalog-063.toml`
- `element-metadata-abi-063.toml`
- `react-migration-disposition-063.toml`
- `interaction-diagnostics-063.toml`
- `interaction-budgets-063.toml`
- `interaction-upgrade-fixtures-063.md`

## Planned gates

| Gate | Requirement | Minimum evidence | Status |
|---|---|---|---|
| `CONTRACT-063` | Trace, profiler, checks, metadata, migration, maturity, and budget contracts are frozen against 0.61/0.62. | Accepted locks and compatibility validation | Planned |
| `TRACE-063` | pytest, browser, CLI, Explorer, and conformance agree on event identity, ordering, outcomes, truncation, and redaction. | Cross-consumer golden/malformed/unknown-version corpus | Planned |
| `PROFILER-063` | Explorer/headless output shows coherent component/action/request/target/state/cache/focus/failure timelines. | Reference recordings and deterministic assertions | Planned |
| `PROFILE-SAFE-063` | Profiling is read-only, access-controlled, bounded, redacted, and explicit about sampling/missing data. | Security/retention/truncation/no-callback tests | Planned |
| `CHECK-063` | Required checks detect the locked unsafe patterns with stable source-linked diagnostics. | Positive/negative/adversarial corpus | Planned |
| `CHECK-SAFE-063` | Analysis is non-executing, deterministic, bounded, cache-safe, and has documented suppressions. | Malicious/huge/cyclic source and repeatability tests | Planned |
| `SOURCE-063` | Explanations connect inferred lifecycle, boundaries, navigation, optimism, identity, and fallback to provenance. | Golden explanation/source-map fixtures | Planned |
| `METADATA-063` | Supported elements publish registry-derived typed props/events/slots/state/lifecycle/fallback/maturity metadata. | Schema and component conformance | Planned |
| `IDENTITY-063` | Wheel, runtime, generated metadata, and optional npm artifact report matching ids/versions/maturity. | Clean-package identity matrix | Planned |
| `MIGRATE-063` | React reports produce native/adapter/redesign/unsupported dispositions with confidence and source spans. | Forms/dashboard/optimism/overlay/router/non-fit corpus | Planned |
| `INTEROP-063` | Any retained React-island recipe remains Experimental, isolated, pinned, CSP-reviewed, SSR-fallback-capable, and cleaned up. | Supply-chain/lifecycle/ownership tests, or accepted omission record | Planned |
| `SECURITY-063` | Traces, reports, metadata, and tools do not expose secrets or cross access/tenant boundaries. | Redaction/access/malformed-input adversarial matrix | Planned |
| `A11Y-063` | Profiler/reports are keyboard, focus, semantics, contrast, zoom/reflow, and reduced-motion usable. | Automated and browser evidence | Planned |
| `PERF-063` | Analysis, trace/profile retention, export, metadata, memory, and CI budgets pass exact/over-limit cases. | Reproducible benchmark/resource report | Planned |
| `CONFORMANCE-063` | Portable fixtures validate supported producers/consumers without executing application callbacks. | Clean conformance runs across package matrix | Planned |
| `DOCS-063` | Tool schemas, findings, suppressions, migration limits, metadata use, and React non-goals match output. | Docs/example/schema checks | Planned |
| `UPGRADE-063` | Older supported traces/configuration fail or adapt predictably and tooling can be disabled without runtime change. | Version/rollback fixtures | Planned |
| `PKG-063` | Clean packages publish matching schemas/maturity and retain no-Node core consumption. | Build/install/identity/reference-app smoke | Planned |

## Release decision

Release requires every Required row Verified, cross-tool trace agreement, deterministic bounded
non-executing analysis, package metadata identity, honest unsupported migration cases, and no secret
leaks. An Experimental React-island recipe may be omitted; its existence cannot block or define the
Supported release.

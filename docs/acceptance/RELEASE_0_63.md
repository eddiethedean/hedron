# Release acceptance: 0.63 theme contract, interaction tooling, and interoperability

**Status:** Proposed / Planned gates  
**Implementation:** [INTERACTION_TOOLING_063](../implementation/INTERACTION_TOOLING_063.md)
**Execution:** [EXECUTION_0_63](../implementation/EXECUTION_0_63.md)

## Planned contract artifacts

- `interaction-capability-inventory-063.toml`
- `theme-resolution-contract-063.toml`
- `theme-export-contract-063.toml`
- `component-parts-manifest-063.json`
- `theme-conformance-contract-063.toml`
- `component-state-matrix-063.toml`
- `visualization-theme-contract-063.toml`
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
| `CONTRACT-063` | Theme resolution/export, component contracts, trace, profiler, checks, metadata, migration, maturity, and budget contracts are frozen against 0.60/0.61/0.62. | Accepted locks and compatibility validation | Planned |
| `THEME-063` | Every supported default component declaration consumes canonical public theme values or a validated compatibility alias; custom themes do not require application CSS. | Dark custom-theme fixture across surfaces, controls, tabs, navigation, and shell chrome | Planned |
| `PALETTE-063` | Interactive states, global link/selection hooks, and bounded responsive recipe conditions derive deterministically with visible provenance. | Light/dark/high-contrast/forced-colors/print/responsive token and recipe corpus | Planned |
| `PARTS-063` | Identity marks, semantic slots, stable parts, state hooks, accessibility requirements, and theme surfaces are typed and registry-derived. | Brand/AccountSummary plus built-in component manifest and metadata matrix | Planned |
| `EXPORT-063` | Resolved themes export to canonical CSS and design-token JSON with matching values, provenance, versioning, and safe rejection. | Runtime/export round-trip, unsafe-value rejection, one-variant and full-package fixtures | Planned |
| `BUNDLE-063` | Base, accessibility, token, and component style bundles have deterministic dependencies and preserve required interaction states. | FastAPI/Flask/Django/Posit/static asset registration and size comparison | Planned |
| `INSPECT-063` | Development inspection exposes token paths, variants, fallbacks, parts, and accessibility overrides without persisting application content. | JSON and human-readable inspection fixtures; production inertness test | Planned |
| `THEME-CHECK-063` | Standalone conformance reports missing tokens, fallback use, contrast, selector coupling, and intentional exceptions. | Deterministic CLI/CI report across component/state/mode catalog | Planned |
| `MATRIX-063` | A portable state-matrix command emits stable component/state/viewport/mode cases and integrates with provider-neutral visual runners. | Focus/hover/disabled/busy/validation/selected/empty/error/permission/dialog/toast corpus | Planned |
| `VISUAL-063` | Visualization roles and Progressive translucent/glass presets share semantic tokens and remain legible in fallback/accessibility modes. | Charts/table fallbacks, patterns/non-color encodings, print/forced-colors/reduced-transparency/browser fallback matrix | Planned |
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
| `SECURITY-063` | Themes, exports, bundles, traces, reports, metadata, and tools do not expose secrets, unsafe CSS, URLs, or cross access/tenant boundaries. | Redaction/access/unsafe-value/malformed-input adversarial matrix | Planned |
| `A11Y-063` | Profiler/reports are keyboard, focus, semantics, contrast, zoom/reflow, and reduced-motion usable. | Automated and browser evidence | Planned |
| `PERF-063` | Theme tokens/manifests/bundles/matrices plus analysis, trace/profile retention, export, metadata, memory, and CI budgets pass exact/over-limit cases. | Reproducible benchmark/resource report | Planned |
| `CONFORMANCE-063` | Portable fixtures validate supported producers/consumers without executing application callbacks. | Clean conformance runs across package matrix | Planned |
| `DOCS-063` | Tool schemas, findings, suppressions, migration limits, metadata use, and React non-goals match output. | Docs/example/schema checks | Planned |
| `UPGRADE-063` | Older supported traces/configuration fail or adapt predictably and tooling can be disabled without runtime change. | Version/rollback fixtures | Planned |
| `PKG-063` | Clean packages publish matching schemas/maturity and retain no-Node core consumption. | Build/install/identity/reference-app smoke | Planned |

## Release decision

Release requires every Required row Verified, complete public theme coverage for supported default
components, runtime/export/inspection/conformance/matrix agreement, cross-tool trace agreement,
deterministic bounded non-executing analysis, package metadata identity, honest unsupported migration
cases, and no secret or unsafe-CSS leaks. Progressive visualization, bundle, and translucent/glass
extensions may be deferred with an explicit disposition; an Experimental React-island recipe may be
omitted. Neither can redefine the Supported release.

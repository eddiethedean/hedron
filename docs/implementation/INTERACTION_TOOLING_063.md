# Phase 0.63: theme contract, interaction tooling, and ecosystem interoperability

**Status:** Required implementation and release evidence landed; Progressive extensions deferred
**Predecessor:** verified 0.61 lifecycle/trace and 0.62 navigation/optimism/failure contracts  
**Authority:** [RFC-0090](../rfcs/RFC-0090-REACTIVE-INTERACTION-PLATFORM.md)  
**Execution:** [EXECUTION_0_63](EXECUTION_0_63.md)
**Acceptance:** [RELEASE_0_63](../acceptance/RELEASE_0_63.md)

The executable packet is [release-gate-0.63.toml](../acceptance/release-gate-0.63.toml), with
machine-readable results in [evidence-063/gate-results-063.json](../acceptance/evidence-063/gate-results-063.json).
Required gates are Verified; per-component bundles, visualization/glass extensions, and the React
island are explicitly Deferred with Supported fallbacks or an accepted omission.

## Outcome

Developers can explain, profile, statically check, test, and migrate Hedron interactions through one
portable contract. A registered custom theme reaches the supported default component stylesheet and
can be exported, inspected, conformance-checked, and exercised through a deterministic state matrix.
Supported Web Components expose typed interoperability metadata, parts, slots, and state hooks.
React migration guidance is automated where facts are knowable and honest where architectural
redesign is required.

## Entry gate

Stage 1 requires frozen upstream schemas plus Stage 0 locks for canonical theme consumption, derived
state provenance, responsive presentation bounds, component parts/slots/state hooks, theme export
identity, conformance and state-matrix coverage, trace compatibility, profiler sampling/retention,
diagnostic catalog and suppressions, source provenance, metadata ABI and package identity, migration
dispositions, security/redaction, performance budgets, and the fate of the Experimental React-island
recipe.

## Candidate public artifacts

| Artifact | Consumer | Contract |
|---|---|---|
| `InteractionTrace` v1 | pytest, browser tests, CLI, Explorer, conformance | Ordered redacted events, stable ids, truncation/missing-data markers. |
| Interaction profile | Explorer/headless export | Component/action/request/target/state/cache/focus/failure timeline with timing provenance. |
| Diagnostic catalog | CLI/CI/Explorer | Stable code, severity, source, explanation, remediation, suppression rules. |
| `Theme resolution` v1 | Runtime/CSS/CLI/Explorer | Canonical tokens, derived values, variants, accessibility modes, fallbacks, and provenance. |
| `Theme export` v1 | Design tools/docs/CI | Versioned CSS and design-token JSON with matching resolved values and safe rejection. |
| `Component contract manifest` v1 | Python/TypeScript/docs/CI | Stable parts, slots, state hooks, accessibility requirements, and supported theme surfaces. |
| `Theme conformance report` v1 | CLI/CI/Explorer | Missing coverage, fallback use, contrast, selector coupling, and remediation. |
| `Component state matrix` v1 | Browser/visual CI | Deterministic component/state/viewport/mode cases with stable machine-readable ids. |
| Element metadata v1 | TypeScript/custom-elements consumers | Properties, events, slots, state owner, lifecycle, fallback, compatibility, maturity. |
| Migration report v1 | CLI/docs/CI | Native/adapter/redesign/unsupported disposition with confidence and source spans. |

## Phase packet and maturity

The fourteen open issues assigned to 0.63 are one packet with two coupled tracks. Theme resolution
and public component contracts are upstream of inspection, conformance, visual coverage, and the
existing interaction tools.

| Track | Issues | 0.63 disposition | Required outcome |
|---|---|---|---|
| Theme foundation | #676, #678, #679, #680 | Required | Canonical token consumption, interactive-state derivation, global link/selection hooks, and bounded responsive recipe conditions. |
| Component contract | #677, #683, #687 | Required | Typed identity marks, semantic slots, stable parts/state hooks, and registry-derived manifest/metadata. |
| Theme evidence | #681, #682, #686, #688 | Required | Conformance, export, development inspection, and deterministic state-matrix evidence. |
| Presentation extensions | #684, #685, #689 | Progressive | Component bundles, accessible visualization primitives, and bounded translucent/glass presets with safe fallbacks. |
| Interaction tooling | Existing 0.63 tooling scope | Required | One trace, profiler, static checks, explanations, migration dispositions, and package conformance. |

Progressive presentation extensions cannot weaken the Required theme contract. Each issue remains
open for its own acceptance criteria, but release status follows the disposition above rather than
issue order alone.

## Static-check inventory

Stage 0 assigns each check a Required/Progressive/Experimental disposition and false-positive corpus.
The Required candidate set includes:

- hidden render I/O or application callback execution during static inspection;
- mutable global request/user state and duplicate state writers;
- unstable collection/component/region identity;
- undeclared or incompatible fragment targets and state transfer;
- missing async/failure/full-navigation fallback;
- unsafe trust-boundary values, redirects, cache variation, or trace fields;
- optimistic mutation without approved risk/revision/idempotency/rollback/conflict behavior;
- unbounded payload, trace, retention, fan-out, retry, polling, or prefetch;
- default stylesheet declarations that bypass public theme tokens or rely on unstable selectors;
- missing component parts, slots, state hooks, theme coverage, fallback provenance, or export parity;
- unsafe CSS values, URLs, selectors, bundle dependencies, or Progressive features used as correctness;
- package metadata/runtime identity mismatch; and
- Progressive capability used as a correctness dependency.

## React migration dispositions

| React pattern | Hedron disposition |
|---|---|
| Form state, server action, pending/error UI | Native mapping to form command + 0.61 lifecycle/boundary. |
| Query/loading/error panel | Native mapping to refreshable view/job/async region. |
| Reducer for server-backed dashboard filters | Native or manual mapping to typed interaction graph and server-owned query state. |
| Error boundary | Native mapping only for declared server/element regions; otherwise manual redesign. |
| Optimistic scalar/list edit | Native only when a 0.62 approved risk class applies. |
| Client router / transition | Manual mapping to server routes + navigation policy. |
| Portal/modal | Map to Hedron overlay ownership where semantics fit. |
| High-frequency canvas, offline-first sync, arbitrary client graph | Unsupported or isolated custom frontend; no false parity claim. |
| Third-party React-only widget | Bounded adapter or Experimental island after lifecycle/security review. |

Automated output never executes source, silently rewrites an application, or claims behavioral
equivalence from syntax alone.

The bounded analyzer is available through `hedron migrate react <path> --format json`; it reports
native, adapter, redesign, and unsupported dispositions with confidence and source spans. The
phase-specific source audit is available through `hedron check --phase-063`, with stable findings,
bounded traversal, deterministic ordering, and repository-local suppressions.

## Theme and tooling workstreams

| ID | Workstream | Deliverables |
|---|---|---|
| W0 | Reconciliation and locks | Upstream schema audit, theme/tooling locks, budgets, dispositions, issue mirrors, and source-of-truth inventory. |
| W1 | Canonical theme resolution | Route every default component declaration through public tokens or validated compatibility aliases; preserve variants and accessibility modes. |
| W2 | Derived states and responsive presentation | Implement deterministic interactive-state derivation, global link/selection hooks, bounded recipe conditions, and provenance. |
| W3 | Component contract surface | Define identity marks, semantic slots, stable parts/state hooks, manifest schema, and generated metadata projections. |
| W4 | Theme exports and bundles | Export resolved CSS/JSON, split base/component bundles with deterministic dependencies, and prove runtime/export parity. |
| W5 | Theme inspection and conformance | Provide development-only inspection, fallback diagnostics, CI conformance, exceptions, contrast checks, and remediation output. |
| W6 | State-matrix and visual extensions | Generate deterministic state matrices; add accessible visualization roles and Progressive translucent/glass presets. |
| W7 | Trace conformance | Canonical encoder/decoder, schema fixtures, unknown-version behavior, redaction/truncation, cross-tool parity. |
| W8 | Interaction profiler | Explorer timeline, filters, timing provenance, payload/cache/focus/failure facts, headless export. |
| W9 | Static analysis core | Non-executing analyzers, stable findings, source maps, deterministic ordering, bounded work/caching. |
| W10 | Check catalog and explanations | Required check corpus, remediation/suppressions, and explanations for lifecycle, boundaries, navigation, optimism, identity, and fallbacks. |
| W11 | Element metadata | Registry-derived schema, TypeScript/custom-elements output, wheel/npm identity, maturity and fallback facts. |
| W12 | Migration and interop | React dispositions, worked native/manual/non-fit examples, and explicit omit versus Experimental island decision. |
| W13 | CI, fleet, and conformance | JSON/SARIF/headless outputs, pytest/browser adapters, package fixtures, first-party adoption, and reference-app diagnosis. |
| W14 | Adversarial closure | Malformed traces/source, unsafe CSS, secrets, huge trees, cyclic metadata, plugin isolation, browser/tool cleanup. |
| W15 | Upgrade and release | Schema/theme compatibility, before/after fixtures, docs, rollback, package parity, and clean-wheel evidence. |

## Profiler invariants

- It is read-only and does not execute application callbacks to fill missing facts.
- Timing shows clock source, sampling, truncation, and unavailable segments.
- Payload values are summarized/redacted; secrets and private content are not retained by default.
- Event identity agrees with pytest, browser, CLI, and conformance consumers.
- Production enablement, retention, and access are explicit policy decisions.

## Metadata and package invariants

- Metadata is generated from the authoritative element/interaction registry, not maintained as a
  competing handwritten list.
- Wheel and any npm artifact report matching component ids, versions, maturity, and compatibility.
- Unsupported/Experimental elements are labeled; metadata existence does not imply support.
- Unknown fields follow version rules, while incompatible ownership/lifecycle semantics fail closed.

## Diagnostics and budgets

Phase 0.63 consolidates upstream diagnostic families and adds `HED-THEME-*`, `HED-CHECK-*`,
`HED-PROFILE-*`, `HED-METADATA-*`, and `HED-MIGRATE-*`. Stage 0 locks token/manifest growth,
stylesheet and export size, state-matrix cardinality, source-tree/check complexity, trace/profile
events and bytes, retention, migration file size, analysis time, memory, cache, concurrency, and CI
overhead. Exact-limit and one-over-limit tests are required. No budget may be bypassed by moving
values into generated CSS, JSON, screenshots, or browser-only diagnostics.

## Compatibility and rollback

- Theme resolution may change generated CSS/assets only through validated public inputs; it does not
  execute application code or change server authority.
- Profiler, checks, inspection, exports, and migration tooling consume public facts and do not execute
  application callbacks or silently rewrite runtime behavior.
- Theme/trace/profile/metadata/migration formats are independently versioned with golden fixtures.
- Static checks begin with explicit maturity/severity and cannot silently become release-blocking.
- Disabling profiler/checks restores pre-0.63 operation without altering application output.
- Core Python users retain a no-Node path; TypeScript metadata generation is a release artifact task,
  not an application install requirement.

## Execution order

1. **E0:** W0 locks and upstream/theme compatibility fixtures.
2. **E1:** W1–W3 canonical theme resolution, derived states, and component contract vertical slice.
3. **E2:** W4–W6 export, inspection, conformance, state-matrix, and Progressive presentation proofs.
4. **E3:** W7 trace conformance across existing consumers.
5. **E4:** W8–W10 profiler, static core, Required checks, and source-linked explanations.
6. **E5:** W11 metadata ABI, package identity, and theme manifest projections.
7. **E6:** W12 migration analyzer and explicit omit/Experimental interop decision.
8. **E7:** W13 CI, fleet, conformance, and reference-app adoption.
9. **E8:** W14–W15 adversarial closure, packaging, rollback, upgrade, and release gate.

## Exit gate

0.63 ships only when all Required `*-063` rows are Verified; every default component declaration is
covered by the public theme contract; runtime, CSS, export, inspector, conformance, state-matrix,
and metadata facts agree; checks are deterministic, bounded, source-linked, and non-executing;
metadata matches packaged runtime identity; migration reports include honest non-fits; secrets
remain redacted; and no Supported path requires React, npm, Node, or a persistent client runtime.

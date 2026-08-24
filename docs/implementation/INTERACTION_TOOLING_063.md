# Phase 0.63: interaction tooling and ecosystem interoperability

**Status:** Proposed / Stage 0 planning  
**Predecessor:** verified 0.61 lifecycle/trace and 0.62 navigation/optimism/failure contracts  
**Authority:** [RFC-0090](../rfcs/RFC-0090-REACTIVE-INTERACTION-PLATFORM.md)  
**Acceptance:** [RELEASE_0_63](../acceptance/RELEASE_0_63.md)

## Outcome

Developers can explain, profile, statically check, test, and migrate Hedron interactions through one
portable contract. Supported Web Components expose typed interoperability metadata. React migration
guidance is automated where facts are knowable and honest where architectural redesign is required.

## Entry gate

Stage 1 requires frozen upstream schemas plus Stage 0 locks for trace compatibility, profiler
sampling/retention, diagnostic catalog and suppressions, source provenance, metadata ABI and package
identity, migration dispositions, security/redaction, performance budgets, and the fate of the
Experimental React-island recipe.

## Candidate public artifacts

| Artifact | Consumer | Contract |
|---|---|---|
| `InteractionTrace` v1 | pytest, browser tests, CLI, Explorer, conformance | Ordered redacted events, stable ids, truncation/missing-data markers. |
| Interaction profile | Explorer/headless export | Component/action/request/target/state/cache/focus/failure timeline with timing provenance. |
| Diagnostic catalog | CLI/CI/Explorer | Stable code, severity, source, explanation, remediation, suppression rules. |
| Element metadata v1 | TypeScript/custom-elements consumers | Properties, events, slots, state owner, lifecycle, fallback, compatibility, maturity. |
| Migration report v1 | CLI/docs/CI | Native/adapter/redesign/unsupported disposition with confidence and source spans. |

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

## Workstreams

| ID | Workstream | Deliverables |
|---|---|---|
| W0 | Reconciliation and locks | Upstream schema audit, profiler/check/metadata/migration locks, budgets, dispositions, issue mirrors. |
| W1 | Trace conformance | Canonical encoder/decoder, schema fixtures, unknown-version behavior, redaction/truncation, cross-tool parity. |
| W2 | Interaction profiler | Explorer timeline, filters, timing provenance, payload/cache/focus/failure facts, headless export. |
| W3 | Static analysis core | Non-executing analyzers, stable findings, source maps, deterministic ordering, bounded work/caching. |
| W4 | Check catalog | Required candidate checks, positive/negative/adversarial corpus, remediation and suppression policy. |
| W5 | Source explanations | Explain lifecycle inference, boundary lowering, navigation, optimism, identity transfer, and fallbacks. |
| W6 | Element metadata | Registry-derived schema, TypeScript/custom-elements output, wheel/npm identity, maturity and fallback facts. |
| W7 | Migration analyzer | React pattern inventory, dispositions/confidence, source-linked report, worked native/manual/non-fit examples. |
| W8 | Interop recipe | Decide omit versus Experimental island; if retained, pin assets and prove isolation/cleanup/SSR fallback/CSP. |
| W9 | CI and conformance | JSON/SARIF/headless outputs, pytest/browser adapters, package fixtures, reproducibility checks. |
| W10 | Fleet adoption | First-party packages publish/consume facts; reference app demonstrates end-to-end diagnosis. |
| W11 | Adversarial closure | Malformed traces/source, secrets, huge trees, cyclic metadata, plugin isolation, browser/tool cleanup. |
| W12 | Upgrade and release | Schema compatibility, before/after fixtures, docs, rollback, package parity, clean-wheel evidence. |

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

Phase 0.63 consolidates upstream diagnostic families and adds `HED-CHECK-*`, `HED-PROFILE-*`,
`HED-METADATA-*`, and `HED-MIGRATE-*`. Stage 0 locks source-tree/check complexity, trace/profile
events and bytes, retention, export size, metadata growth, migration file size, analysis time,
memory, cache, concurrency, and CI overhead. Exact-limit and one-over-limit tests are required.

## Compatibility and rollback

- Tooling consumes upstream public facts; it does not change runtime behavior.
- Trace/profile/metadata/migration formats are independently versioned with golden fixtures.
- Static checks begin with explicit maturity/severity and cannot silently become release-blocking.
- Disabling profiler/checks restores pre-0.63 operation without altering application output.
- Core Python users retain a no-Node path; TypeScript metadata generation is a release artifact task,
  not an application install requirement.

## Execution order

1. **E0:** W0 locks and upstream schema compatibility fixtures.
2. **E1:** W1 canonical trace conformance across existing consumers.
3. **E2:** W2 profiler vertical slice with headless export.
4. **E3:** W3–W4 static core and Required check corpus.
5. **E4:** W5 source-linked explanations.
6. **E5:** W6 metadata ABI and package identity proof.
7. **E6:** W7 migration analyzer and worked examples.
8. **E7:** W8 explicit omit/Experimental interop decision.
9. **E8:** W9–W10 CI, conformance, fleet, and reference-app adoption.
10. **E9:** W11–W12 adversarial closure, packaging, rollback, and release gate.

## Exit gate

0.63 ships only when all Required `*-063` rows are Verified; every tool agrees on trace identity and
outcome; checks are deterministic, bounded, source-linked, and non-executing; metadata matches
packaged runtime identity; migration reports include honest non-fits; secrets remain redacted; and no
Supported path requires React, npm, Node, or a persistent client runtime.

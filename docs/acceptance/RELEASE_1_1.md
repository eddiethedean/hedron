# Hedron `v1.1.0` first-class UI testing acceptance plan

**Status:** Proposed and unscheduled; Stage 0 refinement only
**Baseline:** Published Hedron `v1.0.0`
**Target:** Candidate `v1.1.0`
**Authority:** [RFC-0097](../rfcs/RFC-0097-FIRST-CLASS-UI-TESTING.md)
**Implementation:** [UI_TESTING_1_1](../implementation/UI_TESTING_1_1.md)
**Machine packet:** [release-gate-1.1.toml](release-gate-1.1.toml)

This packet refines a proposed phase; it does not claim implementation, verification, a release
date, or a final public API. Every gate is Planned. There is intentionally no `check_110.py` yet:
W0 must freeze the public contract, schemas, corpus, matrices, and budgets before an executable
checker can be authoritative.

## Entry decision

The predecessor is satisfied because `v1.0.0` is published and its stable testing inventory is the
compatibility baseline. Stage 1 remains blocked on `FREEZE-110`. The freeze must reconcile the
existing render helpers, `AppScenario`, browser hooks, interaction traces, marks/regions,
first-party Playwright fixtures, and test-generation paths before adding a public surface.

The release is an additive testing/tooling phase. It does not change production routing,
rendering, browser assets, HTMX/Alpine/Web Component authority, security defaults, state ownership,
or supported application behavior.

## Gates

| Gate | Required evidence |
|---|---|
| `FREEZE-110` | Complete current-task/source/fixture inventory; fresh-user prototype results; exact public candidate names/signatures; host/maturity matrix; settle and artifact schemas; redaction/error/capture/network policies; reference corpus; measured budgets; zero unresolved authority-changing question |
| `CONTRACT-110` | Render/AppScenario/browser layer boundary; Playwright remains browser authority; no fake DOM, second runner, production instrumentation, broad remote authority, or duplicate locator/action API |
| `HOST-110` | Loopback pre-bound listener, readiness, lifespan, root path, assets, overrides, startup/shutdown failure, interruption, timeout, xdist isolation, external URL and remote authorization behavior; zero leaked resource |
| `LOCATOR-110` | Role/name, label, text, mark, and region lookup; strict ambiguity and dynamic re-query; accessible-first guidance; direct Playwright escape hatch; shadow/specialist-host dispositions |
| `SETTLE-110` | Versioned bounded Hedron-owned settle facts for request/swap/action/lifecycle paths; no global idle claim; deliberate hang diagnostics; zero arbitrary sleeps in maintained examples |
| `ERROR-110` | Correlated server exception, page error, console, request/response, asset, crash, expected-failure, and clean-state behavior; narrow scoped expectations restore deterministically |
| `ARTIFACT-110` | Versioned failure bundle with allowed screenshot/DOM, Playwright trace, semantic/settle/server/browser/environment facts, deterministic layout, redaction, truncation/missing markers, path safety, retention and byte/count budgets, no upload |
| `PYTEST-110` | Optional dependency/import isolation, fixture/options/markers/config precedence, pytest-playwright composition, missing-browser diagnostics, headed/debug/trace workflow, xdist safety, ordinary `pytest` runner |
| `SATELLITE-110` | Every coordinated/optional package has a module/facade/host-provider/protocol-provider/testing-product/private/non-fit disposition; admitted contributions use one explicit versioned central protocol, preserve optional imports and stable compatibility re-exports, package public fixtures, reject conflicts, and never ambiently register pytest plugins or duplicate harness authority |
| `BEHAVIOR-110` | Required PAGE/fragment/OOB/history, form/CSRF/auth, local/request/combined, specialist element, upload/download, action-state, no-JS/failure, root-path, and deliberate-failure corpus |
| `A11Y-110` | Semantic lookup, keyboard/focus/announcement, reduced-motion, forced-colors, zoom/reflow and viewport fixtures; axe provenance/incomplete/error behavior; no automated accessibility-conformance claim |
| `SECURITY-110` | Loopback and remote authorization, network policy, secrets/header/cookie/query/form/trace redaction, synthetic fixture guidance, path/archive safety, browser/context/process isolation, no authorization bypass |
| `PERF-110` | Frozen startup, navigation/probe, settle, memory/process, artifact, shutdown, xdist, and release-matrix budgets with exact-limit/one-over tests and no on-success artifact tax beyond the accepted profile |
| `COMPAT-110` | Stable 1.0 testing inventory and behavior unchanged; base/core installs import without pytest/Playwright/browser; no-Node render/HTTP path; managed/external host and supported dependency matrix reproducible |
| `DOCS-110` | Testing-pyramid guide, installation, first test, failure debugging, trace viewing, CI, remote/security limits, accessibility honesty, troubleshooting, scaffold and review-first generated example |
| `PKG-110` | Clean base/browser/testing-extra wheel/sdist/offline installs, metadata, bounds, import order, missing-extra behavior, browser install instructions, SBOM/notices and reproducible artifacts |
| `RELEASE-110` | Every other Required row Verified; immutable evidence, support/maturity matrix, migration/rollback notes and release approval present; zero skipped Required browser row or contradictory 1.1 claim |

## Required vertical slice

The entry implementation is a synthetic secured profile form in the reference application. It
must prove managed startup, semantic form interaction, an expected validation failure, focus and
announcement behavior, one successful HTMX action/swap, settle and clean assertions, deliberate
failure artifacts, redaction, root-path behavior, and leak-free success/failure/timeout teardown.

The slice begins in Chromium. It is not considered phase evidence until the bounded
Chromium/Firefox/WebKit release corpus and declared host matrix pass.

## Maturity boundary

The phase may promote only the surface supported by evidence. Candidate dispositions are:

- Stable: pytest entry point, managed flagship host, external URL, browser scenario lifecycle,
  semantic marks/regions, cleanup, and the supported failure workflow;
- Beta: versioned settle/artifact schemas and generated browser stubs until downstream experience
  proves compatibility; package testing modules and the contribution protocol until package/fleet
  evidence justifies narrower promotion; and
- Deferred: visual golden comparison, record/replay, remote production testing, a fake widget/DOM
  emulator, and any unproven managed adapter launcher.

W0 may narrow these dispositions. It cannot promote a Deferred item merely by implementing it.

## Prerelease checkpoints

| Checkpoint | Exit evidence |
|---|---|
| `1.1a0` | `FREEZE-110`, prototypes, support/maturity decisions, schemas, corpus, and measured budgets |
| `1.1a1` | Managed host, BrowserScenario vertical slice, semantic locators, settle, error, artifact, and cleanup proof in Chromium |
| `1.1b1` | Pytest/package/scaffold integration, `SATELLITE-110` dispositions/conformance, plus full behavior, security, accessibility, and parallel-execution corpus |
| `1.1rc1` | Three-browser/host/dependency matrix, clean artifacts, compatibility, docs, rollback, and every non-release gate Verified |

## Stop conditions

Stop implementation or promotion if Stage 0 cannot define bounded owned-work settle semantics; the
harness needs production runtime instrumentation; known secrets can enter retained artifacts; a
failure or timeout leaks hosts, ports, contexts, overrides, or files; required browser evidence is
skipped; the optional extra changes base imports; remote capture is ambient; or stable 1.0 testing
behavior changes without a compatible additive path.

If a candidate misses its gate, narrow its maturity or defer it. Do not label raw Playwright setup,
an empty axe result, a Chromium-only smoke, or an artifact screenshot as completion of the phase.

## Release condition

No `v1.1.0` claim is authorized until the machine packet is updated from Planned to Verified by an
accepted checker and immutable evidence. Documentation may describe the proposal only as proposed
and unscheduled before that point.

# RFC-0029: Roadmap to 1.0

**Status:** Accepted

**Revision:** 2026-08-02 — D-031 shifted the pre-1.0 phase numbers down by one without changing their scope, sequence, or gates.

**Revision:** 2026-08-02 — D-032 fixed the phase-to-release mapping and coordinated first-party release train.

**Revision:** 2026-08-03 — D-035 added the 0.6 closure gate, staged 0.7 delivery,
capability-accurate adapters, evidence-backed release gates, a feature-frozen 0.8 baseline, and
published `1.0.0rcN` rehearsals.

## Release strategy

Hedron develops through cumulative, usable phases rather than isolated infrastructure. Phase 0.0 is a documentation baseline with no package publication. Phases 0.1 through 0.8 lead to the 1.0 stability commitment and produce initial release tags `v0.1.0` through `v0.8.0`; phase 1.0 produces `v1.0.0`. Python package versions omit the tag prefix, and first-party distributions use the coordinated release train. Each implementation phase includes public API, implementation, documentation, security, accessibility, testing, performance evidence, and Explorer or CLI visibility where it introduces inference.

The detailed normative scope and exit criteria live in the project [roadmap](../ROADMAP.md).

## Phase and release sequence

| Phase | Initial release | Product outcome |
|---|---|---|
| 0.0 | None | Accepted specification and project foundation |
| 0.1 | `v0.1.0` | Framework-neutral typed rendering core |
| 0.2 | `v0.2.0` | Secure FastAPI and HTMX application MVP |
| 0.3 | `v0.3.0` | HDN, scoped styles, assets, and themes |
| 0.4 | `v0.4.0` | Explorer, CLI, testing, plugins, and component-author platform |
| 0.5 | `v0.5.0` | Intelligent rendering, data components, caching, and utility toolkit |
| 0.6 | `v0.6.0` | Visualization and first-party integration ecosystem |
| 0.7 | `v0.7.0` | Portable adapter foundation, capability-accurate Flask/Django adapters, jobs, and production operations |
| 0.8 | `v0.8.0` | Feature-frozen public API baseline and release hardening |
| 1.0 | `v1.0.0` | Stable supported Hedron release |

Phase 0.7 uses internal gates 0.7A–0.7F without creating additional public roadmap versions. Phase
0.8 publishes the freeze baseline; one or more PEP 440 `1.0.0rcN` prereleases exercise the final
version line before `v1.0.0`.

## Gate

No phase is complete while its acceptance suite, documentation, security review, accessibility requirements, performance evidence, compatibility checks, and reference-application increment remain incomplete. Work may be deferred to a later phase, but partially implemented public contracts do not count toward the phase's initial release.

Phase 0.7 has an additional entry condition: phase 0.6 interaction, cache, fragment, visualization,
browser-runtime, trusted-content, and bounded-data-source contracts must pass the closure gate or be
explicitly reclassified as experimental. Adapter implementation cannot canonize unverified 0.6
behavior as a portable contract.

Beginning with phase 0.8 (`v0.8.0`), no net-new subsystem, adapter, or transport enters the release
line. Public API changes require explicit release-candidate approval and migration analysis. At
phase 1.0 (`v1.0.0`), stable contracts follow semantic versioning and the published deprecation
policy.

## Acceptance criteria

- The roadmap maps every public subsystem to an owner RFC, API contract, implementation spec, and acceptance document.
- Every planned feature has an explicit phase 0.0–1.0 target or a named post-1.0 disposition in the capability ledger.
- All 29 RFCs appear in the RFC-to-phase coverage table.
- Every initial release from `v0.1.0` onward is independently installable, testable, documented, and useful.
- A deprecation and compatibility policy is enforced before phase 0.8 (`v0.8.0`).
- The complete reference application grows cumulatively across releases and passes using packaged artifacts.
- From phase 0.6 closure onward, a completed acceptance item links to an automated test command or
  immutable evidence artifact; checkbox state alone cannot satisfy a release gate.
- Every adapter claim is labeled portable, ASGI, WSGI, or framework-specific and is tested only
  where the underlying framework can provide it.
- `1.0.0` is rehearsed from published `1.0.0rcN` artifacts, including clean install, upgrade,
  deployment, rollback, SBOM, provenance, and vulnerability/license evidence.
- Optional Rust or cross-language work remains post-1.0 unless an accepted RFC changes the decision.

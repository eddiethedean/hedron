# RFC-0029: Capability roadmap

**Status:** Accepted

**Filename note:** The original filename is retained for durable links; D-038 replaces the former
1.0-target framing with an open-ended `0.x` capability roadmap.

**Revision:** 2026-08-02 — D-031 shifted the original pre-1.0 phase numbers.

**Revision:** 2026-08-02 — D-032 fixed the original phase-to-release mapping.

**Revision:** 2026-08-03 — D-035 added the 0.6 closure gate, staged 0.7 delivery,
capability-accurate adapters, and evidence-backed release gates.

**Revision:** 2026-08-03 — D-038 removed the arbitrary 1.0 target and assigned the former deferred
backlog to explicit capability phases 0.9–0.14.

**Revision:** 2026-08-04 — D-041 moved the Jinja replacement and complete HDN removal to 0.9;
native Flask/Django depth moved to 0.11.

**Revision:** 2026-08-07 — D-053 / RFC-0056 add the production-quality maturity program
(phases 0.23–0.25) without scheduling a calendar `1.0` (preserves D-038).

**Revision:** 2026-08-12 — D-058 inserts phase 0.30 for the independently versioned
`fastapi-workbench` 1.0.0 monorepo release and `hedron-workbench` dependency inversion; formerly
planned phases 0.30–0.39 move to 0.31–0.40 without renumbering published phases.

**Revision:** 2026-08-12 — D-061 assigns the unified `hedron-posit` adapter to phase 0.33;
formerly planned phases 0.33–0.40 move to 0.34–0.41 without changing the owned MCP 0.32 packet or
renumbering published phases.

**Revision:** 2026-08-14 — D-066 inserts high-fidelity charts at phase 0.38 and moves the former
0.38–0.41 Web Component capabilities to 0.39–0.42 without renumbering published phases.

## Release strategy

Hedron develops through cumulative, usable capability phases rather than toward a version-number
deadline. Phase 0.0 is a documentation baseline with no package publication. Each implementation
phase `0.N` produces initial release `v0.N.0`; phase 0.10 produces `v0.10.0`. Python package
versions omit the tag prefix, and first-party Hedron distributions use the coordinated release
train. Independently versioned satellites may cut the package version named by their owning
decision: D-058 pairs Hedron `v0.30.0` with `fastapi-workbench` `1.0.0`; D-066 pairs Hedron
`v0.38.0` with `hedron-charts` `0.2.0`. Neither package version declares Hedron `1.0`.

No Hedron 1.0 phase is scheduled. Stability is a per-contract classification backed by compatibility,
deprecation, migration, and evidence obligations; it is not inferred from the distribution version.
The detailed normative scope and exit criteria live in the project roadmap.

## Phase and release sequence

| Phase | Initial release | Product outcome |
|---|---|---|
| 0.0 | None | Accepted specification and project foundation |
| 0.1 | `v0.1.0` | Framework-neutral typed rendering core |
| 0.2 | `v0.2.0` | Secure FastAPI and HTMX application MVP |
| 0.3 | `v0.3.0` | Experimental HDN prototype, scoped styles, assets, and themes |
| 0.4 | `v0.4.0` | Explorer, CLI, testing, plugins, and component-author platform |
| 0.5 | `v0.5.0` | Intelligent rendering, data components, caching, and utility toolkit |
| 0.6 | `v0.6.0` | Visualization and first-party integration ecosystem |
| 0.7 | `v0.7.0` | Portable adapters, jobs, and production operations |
| 0.8 | `v0.8.0` | Hardening, stability classification, and compatibility baseline |
| 0.9 | `v0.9.0` | HDJ standards-first authoring and complete HDN removal |
| 0.10 | `v0.10.0` | Live interaction, focused streaming, and navigation preload |
| 0.11 | `v0.11.0` | Native Flask/Django depth, bounded QuerySet integration, and visual tooling |
| 0.12 | `v0.12.0` | Advanced data editing, distributed sources, and visualization scale |
| 0.13 | `v0.13.0` | Advanced async preparation, concurrency, and observability |
| 0.14 | `v0.14.0` | Portable runtimes and profiling-backed acceleration |

Additional `0.x` phases require an accepted roadmap revision; they are not blocked on declaring a
future major release.

The authoring transition is governed by D-041/D-043/RFC-0031: phase 0.9 removes HDN completely and
adds HDJ, the separate optional versioned `.hdj` format over Jinja/HTML/HTMX, without changing
Python's canonical role. There is no compatibility runtime or converter.

## Gate

No phase is complete while its acceptance suite, documentation, security review, accessibility
requirements, performance evidence, compatibility checks, and reference-application increment
remain incomplete. Work may move to a later phase, but partially implemented public contracts do
not count toward the phase's initial release.

From phase 0.6 closure onward, checked prose is insufficient: completed requirements link to an
automated command or immutable evidence artifact. Each adapter claim is labeled portable, ASGI,
WSGI, or framework-specific and is tested only where the host can provide it.

From the 0.8 compatibility baseline onward, every additive or incompatible change declares its
stability impact, migration obligation, supported matrix, and retained evidence. A phase number
does not automatically promote beta or experimental behavior.

## Acceptance criteria

- Every planned capability has a phase target or an explicitly owned deferred disposition.
- Every initial release from `v0.1.0` onward is independently installable, testable, documented,
  useful, and verified from built or published artifacts as its gate requires.
- New framework, transport, tooling, data, visualization, async, or runtime capabilities have
  explicit non-goals and cannot bypass security, accessibility, performance, or package-isolation
  evidence.
- Compatibility-protected contracts use the numeric deprecation and migration policy even while the
  project remains on the `0.x` line.
- The reference application grows cumulatively and exercises each promoted capability through its
  native deployment path.
- Deferred work retains an owner, rationale, destination phase, and public stability impact.
- A future major-version proposal, if ever useful, requires a separate accepted RFC justified by
  actual compatibility needs rather than roadmap ceremony.

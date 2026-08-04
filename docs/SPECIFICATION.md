# Hedron specification

Maintainer-oriented authority index for RFCs, decisions, and implementation specs.
Adopters should start with [Get started](getting-started/index.md) and
[What's ready today](guides/whats-ready.md). This set also powers the
[Hedron documentation](https://hedron.readthedocs.io/en/latest/).

Hedron is a Python-first, FastAPI-native framework for building typed, server-rendered
component applications with HTML, HTMX, scoped CSS, and optional Web Components—without
requiring Node.js, hydration, a virtual DOM, or a proprietary browser runtime.

## Authority

When documents conflict, use this order:

1. Accepted entries in [DECISIONS.md](DECISIONS.md).
2. Accepted RFCs in [rfcs/](rfcs/README.md).
3. [Foundations](foundations/README.md).
4. Public contracts in [api/](api/README.md).
5. Internal designs in [implementation/](implementation/README.md).

No implementation may silently resolve a specification conflict. It must update the
decision log and affected RFCs first.

## Document sets

- [Vision](foundations/01_VISION.md), [philosophy](foundations/02_PHILOSOPHY.md),
  [design principles](foundations/03_DESIGN_PRINCIPLES.md), and
  [non-goals](foundations/04_NON_GOALS.md)
- [Architecture](ARCHITECTURE.md), [decisions](DECISIONS.md), [glossary](GLOSSARY.md),
  [roadmap](ROADMAP.md), and [project status](STATUS.md)
- [Compatibility](COMPATIBILITY.md), [project layout](PROJECT_LAYOUT.md),
  [engineering baseline](ENGINEERING_BASELINE.md), [configuration](CONFIGURATION.md),
  [diagnostics](DIAGNOSTICS.md), and [identifiers](IDENTIFIERS.md)
- [Reference application](REFERENCE_APPLICATION.md),
  [traceability](https://github.com/eddiethedean/hedron/blob/main/docs/TRACEABILITY.md),
  [readiness report](https://github.com/eddiethedean/hedron/blob/main/docs/READINESS_REPORT.md),
  [contribution process](CONTRIBUTING.md), and
  [cutting a release](RELEASE.md)
- [Architecture RFCs](rfcs/README.md)
- [Public API contracts](api/README.md)
- [Implementation specifications](implementation/README.md)
- [Acceptance suites](acceptance/README.md)

## Coding gate

Coding may begin when:

- the foundational documents have no unresolved contradictions;
- RFCs needed for the first vertical slice are marked Accepted;
- every public API used by that slice has a written contract;
- the relevant implementation and acceptance specifications exist;
- open questions are either resolved or explicitly deferred without destabilizing the slice.

The phase 0.0 readiness sweep satisfied this gate for the phase 0.1 typed rendering core
targeting `v0.1.0`. Phases 0.1 through **0.10** are published and MIT-licensed (D-033);
phase 0.10 ships live interaction (RFC-0032). See [RELEASE.md](RELEASE.md) and
[STATUS.md](STATUS.md).
Later-phase work must still satisfy the owning release gate before implementation begins.

D-041/D-043 and RFC-0031 ship the versioned `.hdj` format through the separate optional
`hedron-jinja` distribution (published in 0.9). Trusted authors retain native HTML, CSS,
JavaScript, Web Components, Jinja, and HTMX after an explicit static feature/capability
prologue; Hedron adds explicit typed/metadata/security bridges. Python components remain
canonical. HDN was removed without a compatibility runtime, converter, or legacy package;
0.8 is the final capable line.

Under D-035, phase 0.7 additionally requires the phase 0.6 behavioral closure gate, accepted
adapter-neutral ownership, resolved package dependency direction, concrete compatibility ranges,
and evidence-backed adapter/operations/jobs/observability ledgers. Phase 0.9 replaced HDN with
HDJ; phase 0.10 delivers live transports; native Flask/Django depth moves to 0.11.
Later work continues through capability-driven `0.x` phases; no 1.0
freeze is scheduled.

The cumulative [reference application](REFERENCE_APPLICATION.md) grows from the phase 0.1
static rendering proof through the phase 0.2 authenticated FastAPI CRUD application into
a secure application with addressable resources, typed actions and forms, DataEditor,
Plotly, scoped styles, and Component Explorer as their owning phases arrive.

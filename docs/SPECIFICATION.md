# Hedron specification

This documentation set is the canonical specification for Hedron and provides a
versioned, internally consistent baseline. It also powers the
[Hedron documentation](https://hedron.readthedocs.io/en/latest/).

Hedron is a Python-first, FastAPI-native framework for building typed, server-rendered
component applications with HTML, HTMX, scoped CSS, and optional Web Components. It aims
for React-like composition and Streamlit-like ease without requiring Node.js, hydration,
a virtual DOM, or a proprietary browser runtime.

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
- [Reference application](REFERENCE_APPLICATION.md), [traceability](TRACEABILITY.md),
  [readiness report](READINESS_REPORT.md), [contribution process](CONTRIBUTING.md), and
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
targeting `v0.1.0`. Phases 0.1 through 0.5 are published and MIT-licensed (D-033);
phase 0.6 is cut-ready as `0.6.0`. See [RELEASE.md](RELEASE.md) and [STATUS.md](STATUS.md).
Later-phase work must still satisfy the owning release gate before implementation begins.

Under D-035, phase 0.7 additionally requires the phase 0.6 behavioral closure gate, accepted
adapter-neutral ownership, resolved package dependency direction, concrete compatibility ranges,
and evidence-backed adapter/operations/jobs/observability ledgers. Phase 0.8 is feature-frozen; final
release rehearsal uses published `1.0.0rcN` artifacts.

The cumulative [reference application](REFERENCE_APPLICATION.md) grows from the phase 0.1
static rendering proof through the phase 0.2 authenticated FastAPI CRUD application into
a secure application with addressable resources, typed actions and forms, DataEditor,
Plotly, scoped styles, and Component Explorer as their owning phases arrive.

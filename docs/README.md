# Hedron specification

This directory is the canonical pre-implementation specification for Hedron. It consolidates the architecture developed in the original design conversation into a versioned, internally consistent baseline.

Hedron is a Python-first, FastAPI-native framework for building typed, server-rendered component applications with HTML, HTMX, scoped CSS, and optional Web Components. It aims for React-like composition and Streamlit-like ease without requiring Node.js, hydration, a virtual DOM, or a proprietary browser runtime.

## Authority

When documents conflict, use this order:

1. Accepted entries in [DECISIONS.md](DECISIONS.md).
2. Accepted RFCs in [rfcs/](rfcs/README.md).
3. [Foundations](foundations/README.md).
4. Public contracts in [api/](api/README.md).
5. Internal designs in [implementation/](implementation/README.md).
6. Historical documents in the [chat archive](../archive/chat-export-2026-08-02/README.md).

No implementation may silently resolve a specification conflict. It must update the decision log and affected RFCs first.

## Document sets

- [Vision](foundations/01_VISION.md), [philosophy](foundations/02_PHILOSOPHY.md), [design principles](foundations/03_DESIGN_PRINCIPLES.md), and [non-goals](foundations/04_NON_GOALS.md)
- [Decisions](DECISIONS.md), [glossary](GLOSSARY.md), [roadmap](ROADMAP.md), and [project status](STATUS.md)
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

The first validation slice is a secure FastAPI CRUD application containing a page, an addressable component, a typed action and form, a DataEditor, a Plotly chart adapter, scoped styles, and the Component Explorer.


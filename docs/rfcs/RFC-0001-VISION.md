# RFC-0001: Vision

**Status:** Proposed

## Summary

Hedron is a typed server-component framework for Python web applications. Its flagship experience extends FastAPI and produces standard HTML enhanced with HTMX and optional Web Components. It offers component composition and intelligent Python-object rendering without a mandatory Node.js toolchain.

## Requirements

- A new FastAPI user renders a useful secure page within five minutes.
- Common CRUD, form, data, and dashboard work is possible with Python components alone.
- Advanced users can control markup with HDN, presentation with scoped CSS, and browser behavior with Web Components.
- All inferred behavior is visible in the Explorer or CLI.
- Existing FastAPI applications can adopt Hedron incrementally.
- Flask and Django can reuse core semantics through dedicated adapters.

## Positioning

The public message is “typed component-based FastAPI interfaces without Node.js,” not “React in Python.” React familiarity is a learning aid, Streamlit is an ergonomics reference, and HTMX is an interaction mechanism; none defines Hedron’s runtime model.

## Acceptance criteria

- The reference application demonstrates a page, fragment, form, action, addressable component, rich browser widget, and inspected inference.
- The application remains understandable through emitted HTML, HTTP routes, and FastAPI metadata.
- The onboarding guide introduces no compiler or AST concepts.


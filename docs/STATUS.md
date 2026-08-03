# Specification status

**Baseline:** 0.1 pre-implementation  
**Date:** 2026-08-02  
**Implementation:** not started

The architecture is frozen enough to prepare a first vertical slice, but RFC acceptance remains the formal coding gate. The documents currently describe the intended 1.0 shape and distinguish MVP requirements from deferred capabilities.

## Current conclusions

- Python is the reference implementation.
- FastAPI is the flagship integration and its documented extension points are authoritative.
- `hedron-core` remains independent of ASGI, WSGI, FastAPI, Flask, and Django.
- HTML endpoints return components; JSON endpoints return models.
- Addressability is explicit and preserves framework-native security dependencies.
- HTMX is the default server-interaction layer; Web Components own durable browser-local behavior.
- HDN, scoped styles, Explorer, DataEditor, integrations, and async boundaries have defined architectures.
- Rust and cross-language runtimes are deferred until Python semantics stabilize and profiling supplies evidence.

## Before the first code commit

1. Review RFC-0001 through RFC-0009 and RFC-0012.
2. Resolve the open questions listed in [DECISIONS.md](DECISIONS.md).
3. Mark the vertical-slice RFCs Accepted.
4. Select supported Python and FastAPI version ranges.
5. Select the package namespace and repository layout.


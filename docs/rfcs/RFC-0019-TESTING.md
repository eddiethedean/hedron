# RFC-0019: Testing

**Status:** Proposed

## Layers

- Pure component and serializer unit tests.
- Snapshot tests for HTML, manifests, HDN programs, styles, OpenAPI, and chart specifications.
- Adapter conformance tests for routing, dependencies, security, and response behavior.
- HTTP tests with FastAPI/httpx clients.
- Browser tests for HTMX, Web Components, keyboard behavior, and accessibility.
- Security, performance, compatibility, and packaging suites.

Public helpers include component rendering assertions, route lookup, fragment requests, dependency overrides, named examples, normalized snapshots, and async clients compatible with pytest-anyio.

Snapshots normalize only documented nondeterminism. They must not hide ordering errors, unsafe escaping, missing attributes, or unstable identifiers. Browser and visual tests complement rather than replace semantic assertions.

## Acceptance criteria

- Every accepted RFC maps to at least one acceptance document and automated suite.
- The reference application runs against released packages, not repository-only imports.
- Tests cover sync/async parity, cancellation cleanup, security boundaries, and optional-dependency absence.
- Accessibility checks combine static rules, axe-style browser analysis, and manual keyboard scenarios.


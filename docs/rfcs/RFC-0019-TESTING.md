# RFC-0019: Testing

**Status:** Accepted

## Layers

- Pure component and serializer unit tests.
- Snapshot tests for HTML, manifests, styles, OpenAPI, chart specifications, and optional Jinja
  template output and metadata.
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

## Phase 0.14 portable conformance kit

Phase 0.14 publishes a language-neutral conformance-test kit (`hedron-conformance`) with
versioned machine-readable fixtures, golden render/diagnostic artifacts, negative cases, and a
capability-level runner. Fixture versioning and normalization rules are public so implementations
cannot pass merely by matching incidental CPython formatting. Experimental Java and Node runtimes
and optional native accelerators are tested through the published kit in addition to native unit
tests; failures identify the fixture, contract version, and violated capability (D-048).

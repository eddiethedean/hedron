# Roadmap to 1.0

## Phase 0 — Specification gate

- Accept foundations and RFC process.
- Resolve supported runtime versions and repository/package layout.
- Accept the core, component, FastAPI, routing, HTMX, security, testing, and packaging RFCs.
- Freeze the public contracts required by the first slice.

## Phase 1 — Secure vertical slice

- Component node tree and contextual HTML serializer.
- Hedron-owned models and fields.
- `HedronRoute`, `HedronRouter`, component response classes, and OpenAPI metadata.
- Pages, explicit addressable components, typed actions, forms, HTMX page/fragment handling.
- Secure headers, CSRF integration, safe URLs, trusted HTML boundary, private authenticated caching defaults.
- Registry, CLI inspection, minimal Explorer, tests, and examples.

Exit criterion: a secure authenticated CRUD application works using documented public APIs.

## Phase 2 — Authoring system

- HDN parser, type checking, diagnostics, source maps, inspect/eject workflow.
- Scoped CSS compiler, asset manifest, external fingerprinted bundle, theme tokens.
- Component folder discovery, examples, documentation, and development reload.

## Phase 3 — Data application proof

- `Auto()`, Data Intelligence metadata, `DataTable`, and `DataEditor`.
- Narwhals normalization and paged data-source protocols.
- Tabulator Web Component, typed changes, conflict handling, authorization, and Explorer Data panel.
- Matplotlib, Plotly, and Altair adapters with accessibility and payload policies.

## Phase 4 — Ecosystem and adapters

- Markdown, code, images, email, SQLAlchemy, and Authlib integrations.
- Flask and Django distributions with conformance suites.
- Plugin packaging, compatibility checks, and supply-chain diagnostics.

## Phase 5 — Operational maturity

- Async tracing, single-flight caches, job-backend protocol, production diagnostics.
- Accessibility, security, and performance budgets enforced in CI.
- Stable upgrade policy and deprecation tooling.

## Phase 6 — 1.0 readiness

- Public API stability review.
- Complete reference application and deployment guides.
- Cross-adapter conformance and compatibility matrix.
- Security review, performance baselines, accessibility audit, and release checklist.

## Post-1.0 candidates

SSE, WebSocket components, streamed documents, advanced data grids, React migration analysis, cross-language specifications, and optional Rust acceleration require separate accepted RFCs and demonstrated demand.


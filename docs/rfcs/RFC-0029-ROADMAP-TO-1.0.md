# RFC-0029: Roadmap to 1.0

**Status:** Proposed

## Release strategy

Hedron develops through vertical slices rather than isolated infrastructure. Each slice includes public API, implementation, documentation, security, accessibility, testing, and Explorer visibility.

## Milestones

1. **Core:** models, node tree, serializer, registry, FastAPI routes and responses.
2. **Interaction:** pages, addressable components, actions, forms, HTMX, security, minimal Explorer.
3. **Authoring:** HDN, scoped styles, assets, themes, inspect/eject, CLI build.
4. **Data:** `Auto`, DataTable, DataEditor, sources, Matplotlib, Plotly, Altair.
5. **Ecosystem:** optional content and service integrations, plugins, Flask and Django conformance.
6. **Operations:** async diagnostics, caching, jobs, deployment, performance and supply-chain review.
7. **1.0:** stable public API, compatibility policy, migration guidance, audited reference application, and release gates.

## Gate

No milestone is complete while its acceptance suite, documentation, security review, accessibility requirements, and representative example remain incomplete. Features outside the milestone require a separate RFC and cannot delay the core with speculative abstraction.

## Acceptance criteria

- The roadmap maps every public subsystem to an owner RFC, API contract, implementation spec, and acceptance document.
- A deprecation and compatibility policy exists before the first stable release candidate.
- Optional Rust or cross-language work remains post-1.0 unless an accepted RFC changes the decision.


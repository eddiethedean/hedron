# RFC-0077: Explorer architecture and operator-grade development tooling

## Summary

`hedron-explorer` should move from a monolithic router concentration into a modular,
service-oriented architecture with shared services for browser and headless diagnostics.

## Scope

1. Decompose transport and service layers so Explorer remains thin at the router boundary.
2. Introduce a versioned `ExplorerProvider` protocol with declared capabilities,
   per-provider constraints, redaction policy, and bounded payload semantics.
3. Add resilient query paths (search, filter, pagination/virtualization) for large
   registries.
4. Align browser and CLI/JSON outputs through shared model services.
5. Add bounded interaction-lab and package-health surfaces without new authority
   claims.

## Non-goals

- Reclassifying `EXPLORER-10-001` into a live trace contract.
- Turning the Explorer into a production default endpoint.
- Requiring Node to run or run full audits from a durable cross-process audit buffer.

## Decision

This phase is tracked as D-085 and implemented through phase 0.50 release gates.

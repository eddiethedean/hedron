# Architectural decisions (index)

Hedron records product and architecture choices as numbered decisions **D-001…**.
The full authoritative table lives in the repository (not duplicated here):

**[docs/DECISIONS.md on GitHub](https://github.com/eddiethedean/hedron/blob/main/docs/DECISIONS.md)**

## Recent decisions (adopter-relevant)

| ID | Topic |
|---|---|
| D-104 | Phase 0.59 conditional Stage 0 locks DesignSystem, palette v1, recipes/scopes, schemas, precedence, budgets, starter adoption, gates, and the final-0.58 audit blocker |
| D-103 | Progressive styling authoring and inspectable design systems own phase 0.59, including brand/recipe/scope lowering and migration of every styling starter (RFC-0086) |
| D-102 | Phase 0.58 Stage 0 locks signatures, lowering, schemas, security, host dispositions, budgets, scaffolds, starter adoption, tracking, gates, and upgrades |
| D-101 | Progressive feature authoring and inspectable lowering own phase 0.58, including migration of every inventoried starter example to the highest applicable abstraction (RFC-0085) |
| D-100 | Phase 0.57 Stage 0 locks finite presentation/CSP/semantics/parity/upgrade contracts without runtime or version changes |
| D-099 | Unified styling, presentation, and zero-application-CSS own phase 0.57 (RFC-0084; [#558](https://github.com/eddiethedean/hedron/issues/558)–[#570](https://github.com/eddiethedean/hedron/issues/570)) |
| D-070 | Production-grade Web Component platform graduation owns 0.42 Stage 0 (RFC-0060; [#97](https://github.com/eddiethedean/hedron/issues/97)) |
| D-069 | Typed browser composition, draft transfer, and navigation own Published 0.41 (RFC-0060; [#96](https://github.com/eddiethedean/hedron/issues/96)) |
| D-068 | Web Component authoring / React migration matrix own Published 0.40 (RFC-0060; [#95](https://github.com/eddiethedean/hedron/issues/95)) |
| D-067 | Rich data / OptimisticMutation own Published 0.39 (RFC-0060; [#94](https://github.com/eddiethedean/hedron/issues/94)) |
| D-066 | High-fidelity charts own 0.38; later Web Component phases move to 0.39–0.42 (RFC-0069; [#251](https://github.com/eddiethedean/hedron/issues/251)) |
| D-065 | Form-associated elements, InteractionState, gesture/overlay primitives, and high-severity remediations #230–#237 own 0.37 |
| D-064 | Web Component ABI and lifecycle foundation owns published 0.37 |
| D-061 | Schedule unified `hedron-posit` for 0.33; move Gradio, fleet closure, and the Web Component program down to 0.34–0.41 without changing MCP 0.32 |
| D-060 | Production-grade deny-by-default MCP projection (`hedron-mcp` `0.2.0` Beta at cut; 0.32; RFC-0065) |
| D-059 | Production-grade developer/portable tooling + Streamlit AST migrator (0.31; RFC-0064 / RFC-0061) |
| D-058 | `fastapi-workbench` monorepo ownership and independent 1.0.0 release; `hedron-workbench` dependency inversion (0.30); later planned phases shift to 0.31–0.40 |
| D-057 | Production-grade Posit Workbench deployment adapter (`hedron-workbench`, 0.29) |
| D-051 | Production security floor (0.20) + CSRF / `SecurityPolicy` composition (0.22) |
| D-052 | Human AT protocol packet (0.21); sessions still Planned |
| D-053 | Production-quality maturity program (0.23–0.25 packets) |
| D-050 | Accessibility engineering / progressive enhancement (0.19) |
| D-049 | Model demos / inference workflows (0.18) |
| D-046 | Flask/Django native depth (0.11) |
| D-043 / D-041 | HDJ / HDN authoring break (0.9) |

## How decisions relate to docs

| Layer | Role |
|---|---|
| Decisions | Binding product/architecture choices |
| RFCs | Design detail (maintainer corpus on GitHub under `docs/rfcs/`) |
| [What’s ready](whats-ready.md) | Authoritative adopter capability-maturity page |
| [STABILITY](../api/STABILITY.md) | API compatibility levels |

Contributors: follow [Contributing](../CONTRIBUTING.md) before proposing a decision or RFC.

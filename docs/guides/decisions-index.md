# Architectural decisions (index)

Hedron records product and architecture choices as numbered decisions **D-001…**.
The full authoritative table lives in the repository (not duplicated here):

**[docs/DECISIONS.md on GitHub](https://github.com/eddiethedean/hedron/blob/main/docs/DECISIONS.md)**

## Recent decisions (adopter-relevant)

| ID | Topic |
|---|---|
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

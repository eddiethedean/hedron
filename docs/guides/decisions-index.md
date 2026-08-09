# Architectural decisions (index)

Hedron records product and architecture choices as numbered decisions **D-001…**.
The full authoritative table lives in the repository (not duplicated here):

**[docs/DECISIONS.md on GitHub](https://github.com/eddiethedean/hedron/blob/main/docs/DECISIONS.md)**

## Recent decisions (adopter-relevant)

| ID | Topic |
|---|---|
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
| [What’s ready](whats-ready.md) | Adopter capability maturity SSOT |
| [STABILITY](../api/STABILITY.md) | API compatibility levels |

Contributors: follow [Contributing](../CONTRIBUTING.md) before proposing a decision or RFC.

# REVIEW-032 security review brief

**Baseline:** Published `v0.31.0` tip; Experimental Alpha `hedron-mcp` `0.1.x`
(RFC-0043 / `MCP-017`).
**Package at cut:** `hedron-mcp` `0.2.0` Beta (Supported inventory only).
**Owning decision:** D-060 / RFC-0065.
**Tracking:** [#89](https://github.com/eddiethedean/hedron/issues/89).

## Trust boundaries in scope

1. Deny-by-default registration (install/mount/zero registrations → empty server)
2. Host authentication reuse and application-owned authorization/tenancy hooks
3. Confused-deputy tool execution vs underlying HTTP/UI/job actions
4. Identifier enumeration and cross-tenant observation via resources/tools
5. Authority widening across HTTP, UI, job, resource, and tool surfaces
6. Mutation enablement, idempotency/replay, and audit completeness
7. Prompt/tool metadata redaction and data exfiltration via resource schemas
8. Origin/transport/session lifecycle, SSRF/path traversal via file/URI tools
9. Rate/size/concurrency/deadline/cancel/disconnect bounds under multi-worker deploy
10. Multi-client adversarial suites against the documented supported-client matrix

## Out of scope

- Gradio / Hugging Face client interoperability (phase 0.34 under D-061)
- Making Hedron an identity provider, secrets broker, or approval system
- Commercial SLA / certification / Hedron `1.0`
- Vendor-specific MCP extensions left Experimental at cut
- Web Component platform (0.36–0.41 under D-061)

## Adversarial suite

Planned: `tests/security/test_mcp_adversarial.py` (and related multi-worker /
multi-client fixtures owned by `AUTHZ-032` / `BOUNDS-032`).

## Methodology

Structured maintainer-led review independent of the feature-authoring pass
(external firm optional). Findings land in `DISPOSITION.toml` and
`REDACTED_REPORT.md` at cut.

## Packet status

**Verified** — see `REDACTED_REPORT.md` and `DISPOSITION.toml` (`critical_high_open = false`).

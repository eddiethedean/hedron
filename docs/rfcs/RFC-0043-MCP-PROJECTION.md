# RFC-0043: Optional MCP projection (`hedron-mcp`)

**Status:** Accepted
**Phase:** 0.17 (`v0.17.0`)
**Stability:** `experimental` (API and distribution); package maturity Alpha until exit evidence
**Evidence:** `MCP-017`, `PKG-017`
**Package:** optional `hedron-mcp` distribution (D-015); Streamable HTTP; disabled and empty by
default
**Related:** [Plotly Dash feature cross-check](../PLOTLY_DASH_FEATURE_CROSSCHECK.md) (Dash MCP);
RFC-0012, RFC-0014, RFC-0016; Gradio MCP notes deferred to 0.18 composition

**Graduation ownership:** Production-grade exit for the declared Supported inventory is
owned by phase **0.32** / [RFC-0065](RFC-0065-PRODUCTION-GRADE-MCP.md) / D-060
([#89](https://github.com/eddiethedean/hedron/issues/89)). This RFC remains the Alpha
product contract; it is not the 0.32 graduation packet.

## Summary

Define an optional `hedron-mcp` distribution that projects only explicitly opted-in page/component/
data resources and typed action/function tools to MCP clients over Streamable HTTP. Authentication,
authorization, tenant filtering, scopes, read-versus-mutate effects, confirmation, schemas, limits,
deadlines, cancellation, rate limits, audit/correlation, redaction, prompt-injection diagnostics,
deployment prefixes, and disconnect behavior are part of the contract. MCP never grants authority
beyond the authenticated principal; enabling MCP does not expose every page or action.

## Motivation and background

Dash MCP (and Gradio’s MCP server) show agent-interface demand. Dash’s broad default exposure is
unacceptable for Hedron. Hedron needs a deny-by-default projection of the same explicit domain
actions already used by HTTP/HTMX UIs.

## Proposed design

- Separate optional distribution `hedron-mcp` importing as `hedron_mcp`.
- Default: disabled and empty (no resources, no tools).
- Opt-in registration for resources (pages, component metadata, data descriptions, Explorer/OpenAPI
  schemas — never raw process objects or source by default) and tools (explicit actions or
  separately decorated typed functions).
- Transport: Streamable HTTP with deployment-prefix, origin, session, and disconnect conformance.
- Same authn/authz/tenant/rate/deadline/cancel/side-effect/confirmation policy as the underlying
  application action.
- Redacted descriptions; stable public tool names; audit records; correlation IDs; clear
  read-only vs mutating classification.
- Diagnostics for accidental sensitive schemas, hidden-value authorization, over-broad enumeration,
  prompt-injection-bearing content, and tools whose declared effects disagree with their
  HTTP/action contract.

## Alternatives considered

1. **Auto-expose all routes/actions when MCP is installed.** Rejected — Dash-shaped default hazard.
2. **Ship MCP inside `hedron` core.** Rejected — D-015; keeps agent surface optional.
3. **Wait for Gradio interoperability (0.18).** Rejected — Dash audit already justifies a Hedron-owned
   deny-by-default projection in 0.17; 0.18 may compose with it.

## Security implications

Prompt injection via resources, confused-deputy tools, tenant crossover, and over-broad discovery
are primary threats. Deny-by-default, principal-bounded authz, redaction, rate/payload limits, and
audit are mandatory. UI option filtering is not authorization.

## Accessibility implications

MCP is a machine interface; human-facing docs and Explorer labels must still mark experimental
status and effect classification clearly.

## Performance implications

Rate and payload limits; cancellation and disconnect tests; no unbounded resource enumeration.

## Testing strategy

Discovery, schemas, authn/authz, tenant isolation, redaction, read/mutate classification, rate and
payload limits, cancellation, disconnect, adversarial tool inputs, prompt-injection-bearing
resources, audit records, and disabled/default-empty behavior. Gate: `MCP-017`.

## Compatibility and migration

Optional package. Dash MCP maps to explicit opt-in tools/resources (`MIGRATE-017`). Enabling the
package without registrations remains a no-op empty server.

## Open questions

None blocking Acceptance. Exact MCP SDK pin is an implementation detail behind the public contract.

## Acceptance criteria

- Default install/enable path exposes zero tools and zero resources.
- Mutating tools require the same confirmation/authz as the underlying action.
- Conformance suite covers the security cases above before Supported claims (Supported ≠ default;
  experimental until evidence promotes).

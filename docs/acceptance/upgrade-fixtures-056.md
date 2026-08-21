# Upgrade fixtures for phase 0.56

**Source train:** Published in-tree `v0.55.0`<br>
**Target:** `v0.56.0`<br>
**Authority:** D-097 / D-098 / RFC-0083

## Compatibility expectations

- Existing `SecurityPolicy.from_name("development"|"standard"|"strict")` continues
  to resolve; 0.56 may tighten defaults but never silently inherits development
  settings in production.
- Public `SafeUrl`, `TrustedHtml`, `Secret`, CSRF, audit, and package-policy APIs
  retain compatibility paths and delegate to shared authorities where applicable.
- 0.55 `IdempotencyPolicy` / capabilities / upload / CSP paths remain valid;
  signed intents compose with them and do not replace CSRF or object-level authz.
- Package-local egress validators (maps / Gradio / MCP) become adapters over core
  `EgressPolicy` with equivalent or intentionally stricter outcomes.

## Fixture themes

1. Preset mapping and composition field defaults.
2. Sink decisions for URL / HTML / selector / SVG corpora unchanged or stricter.
3. CSRF + replay + intent ordering on high-risk mutations.
4. Budget nesting: upload/workflow/stream charges charge a parent `RequestBudget`.
5. Context serialization reject broadened / foreign / client-supplied authority.

# REVIEW-026 security review brief

**Baseline:** Published `v0.25.2` Supported inventory
([production-grade-inventory-026.toml](../production-grade-inventory-026.toml)).
**Packages:** `hedron-core`, `hedron`, `hedron-explorer`.
**Owning decision:** D-054 / RFC-0057.

## Trust boundaries in scope

1. HTML escaping / trusted types boundary in the renderer
2. Fragment / OOB authorization and region allowlists
3. CSRF / session composition on FastAPI
4. Build / static asset serving
5. Plugin discovery surface
6. Job observation / status polling (not SSE)
7. Explorer exposure (development vs secured vs off; production refusal)

## Out of scope

- Commercial SLA / certification claims
- Promoting experimental live transports
- Packages deferred to 0.27+ (data, Flask/Django, charts, MCP, Gradio)

## Adversarial suite

`tests/unit/test_review_026_adversarial.py` — required green for `REVIEW-026`.

## Methodology

Structured review of the frozen CONTRACT-026 inventory against the boundaries
above, independent of the feature-authoring pass for this packet. Findings and
dispositions are recorded in `DISPOSITION.toml` and summarized in
`REDACTED_REPORT.md`. External commercial re-review remains optional follow-up.

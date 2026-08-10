# REVIEW-027 security review brief

**Baseline:** Published `v0.26.0` Supported inventories
([production-grade-inventory-027.toml](../production-grade-inventory-027.toml)).
**Packages:** `hedron-data`, `hedron-flask`, `hedron-django`, `hedron-jinja`,
`hedron-extras`.
**Owning decision:** D-055 / RFC-0058.

## Trust boundaries in scope

1. Data query / write / export bounds and spreadsheet paths
2. Adapter fragment / OOB authorization under host-owned sessions/CSRF
3. HDJ strict sinks, prologue validation, and CSP/assets reconciliation
4. Curated extras discovery quarantine (`experimental-ui` fail-closed)
5. Portable PAGE/FRAGMENT / header parity across FastAPI, Flask, and Django

## Out of scope

- Commercial SLA / certification claims
- Promoting experimental live transports
- Making Explorer audit durable (`REV-026-003` remains Explorer-owned)
- Charts / native / MCP / Gradio (later phases)

## Adversarial suite

`tests/unit/test_review_027_adversarial.py` — required green for PARITY-027 /
PKG-027 evidence.

## Methodology

Structured maintainer-led review of the frozen CONTRACT-027 inventory against the
boundaries above, independent of the feature-authoring pass for this packet.
Findings and dispositions are recorded in `DISPOSITION.toml` and summarized in
`REDACTED_REPORT.md`. External commercial re-review remains optional follow-up.

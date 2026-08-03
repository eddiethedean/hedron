---
status: shipped
---

# Explorer API

**Status:** Accepted for phase 0.4

`hedron-explorer` mounts under `/hedron-explorer` when `explorer` is `development` or `secured`.

## Surfaces

- HTML shell with HTMX navigation across components, routes, graph, security, accessibility, packages, and settings.
- JSON APIs under `/hedron-explorer/api/*` return sanitized registry views (no secrets, no absolute paths as live data).
- Preview renders through the production renderer and attaches the active build manifest when present.
- Request simulation is allowlisted and mutation-safe by default (`allow_mutations=false`).

## Guarantees

Registry identifiers only; redaction; rate limiting and audit hooks in secured mode; keyboard-operable shell.

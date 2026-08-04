---
status: shipped
---

# Explorer API


!!! note "Stability (0.8 freeze)"

    Classifications for this surface are recorded in [STABILITY.md](STABILITY.md). Package maturity (Beta/Alpha) is separate from API level (`beta` / `experimental` / `internal` / `deferred`).

**Status:** Accepted for phase 0.4

`hedron-explorer` mounts under `/hedron-explorer` when `explorer` is `development` or `secured`.

## Surfaces

- HTML shell with HTMX navigation across components, routes, graph, security, accessibility, packages, and settings.
- JSON APIs under `/hedron-explorer/api/*` return sanitized registry views (no secrets, no absolute paths as live data).
- Preview renders through the production renderer and attaches the active build manifest when present.
- Request simulation is allowlisted and mutation-safe by default (`allow_mutations=false`).

## Guarantees

Registry identifiers only; redaction; rate limiting and audit hooks in secured mode; keyboard-operable shell.

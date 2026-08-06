# RFC-0042: Server-side notebook preview (`hedron-notebook`)

**Status:** Accepted
**Phase:** 0.17 (`v0.17.0`)
**Stability:** `experimental` (API and distribution); package maturity Alpha until exit evidence
**Evidence:** `NOTEBOOK-017`, `PKG-017`
**Package:** optional `hedron-notebook` distribution (D-015); not the 0.16 browser-Python /
JupyterLite sandbox
**Related:** [Plotly Dash feature cross-check](../PLOTLY_DASH_FEATURE_CROSSCHECK.md) (Jupyter
display); RFC-0014, RFC-0028

## Summary

Define a development-oriented server-side `hedron-notebook` preview helper that runs a normal
Hedron application from an authoring notebook with inline iframe and external-link modes,
configurable dimensions, proxy/root-path detection, random port/session token, error forwarding,
clean shutdown, collision handling, and explicit warnings for hosted or publicly reachable
notebooks. It must not become an accidental Supported production server.

## Motivation and background

Dash’s Jupyter inline/external/tab display is a real authoring gap. The 0.16 isolated
browser-Python sandbox solves a different problem (client-side execution without server/session
access). Authors still need to preview a real Hedron ASGI app from a notebook during development.

## Proposed design

- Separate optional distribution `hedron-notebook` importing as `hedron_notebook`.
- Preview helper starts a local server with random port and unguessable session token.
- Modes: inline iframe and external link/tab; configurable dimensions.
- Detect proxy / root-path prefixes; forward server errors to the notebook UI safely (no secret
  leakage).
- Clean shutdown, port collision handling, multi-preview isolation.
- Hard warnings when the environment is hosted or publicly reachable; default guidance is
  localhost-only development.
- Distinct from and non-substituting for the 0.16 JupyterLite/Pyodide sandbox.

## Alternatives considered

1. **Only document uvicorn + notebook manual steps.** Rejected — too error-prone for the audited gap.
2. **Reuse Dash’s notebook display protocol.** Rejected — couples to React callback runtime.
3. **Ship preview inside `hedron` core.** Rejected — keeps flagship free of notebook process tooling
   (D-015).

## Security implications

Token leakage, hostile notebook HTML in iframes, open ports on shared hosts, and accidental
production exposure are primary threats. Random tokens, localhost defaults, teardown guarantees,
and hosted-environment warnings are mandatory. Preview never weakens CSRF/authz of the previewed
app.

## Accessibility implications

Iframe/link modes must remain keyboard-reachable; document limitations of embedded previews.

## Performance implications

Port reuse and multi-preview tests; teardown must not leak processes. Not a load-bearing
production path.

## Testing strategy

Proxy prefixes, token leakage, hostile notebook HTML, port reuse, server failure, multiple
previews, teardown, hosted-environment warnings. Gate: `NOTEBOOK-017`.

## Compatibility and migration

Optional package only. Dash Jupyter display maps here in migration inventory (`MIGRATE-017`).

## Open questions

None blocking Acceptance. Exact Jupyter frontend packaging (classic vs JupyterLab widget) may be
resolved during implementation without changing the security contract.

## Acceptance criteria

- Preview tests cover the threat cases above; no preview path is labeled Supported production.
- Install isolation: core/`hedron` wheels do not require `hedron-notebook`.
- Docs clearly separate notebook preview from the 0.16 browser-Python sandbox.

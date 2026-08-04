# Component Explorer acceptance

## Phase 0.2 preview (`v0.2.0`)

- [x] Development preview mounts at `/hedron-explorer/` when `explorer="development"` (including under `security="standard"`).
- [x] Explorer is absent when `explorer="off"` (default production posture).
- [x] `explorer="secured"` rejects anonymous requests (requires `request.state.hedron_authenticated` or supplied dependencies).
- [x] Preview lists registry routes/components and static security findings; secrets and absolute paths are not echoed as live data.

## Full Explorer coverage *(phase 0.4)*

- [x] Components, routes, graph, source, styles, assets, security, accessibility, packages, and settings have defined views.
- [ ] Dedicated pages/actions/examples/HTMX panels beyond the shared shell. *(Deferred — covered by routes + component detail for 0.4)*
- [x] Preview uses the production renderer (sandboxed iframe) and redacts absolute paths.
- [x] Automatic route, target, swap, style, and asset decisions include human-readable explanations (CLI `preview`/`inspect` and Explorer inference panel).
- [x] Dependency overrides and sample data are isolated and reset between examples (`hedron.testing.override_dependencies`).

## Security and accessibility

- [x] Explorer routes are absent in production by default (`explorer="off"`).
- [x] Production opt-in requires authorization, redaction, rate limiting, and audit logs. *(secured mode)*
- [x] Arbitrary paths, modules, URLs, headers, and unregistered identifiers cannot be submitted. *(CSS reads are allowlisted under component roots; simulate rejects unknown keys / bad JSON.)*
- [x] Mutation simulation is disabled by default.
- [x] The interface is keyboard operable and passes declared accessibility checks.
- [x] Explorer static assets are served through the secured router (not a bare StaticFiles mount).

## Exit

Phase 0.4 Explorer shell panels, secured controls, and inference explanations are covered by integration and unit suites. Dedicated pages/actions/examples/HTMX panels remain deferred.

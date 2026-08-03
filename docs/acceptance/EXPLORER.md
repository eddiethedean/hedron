# Component Explorer acceptance

## Phase 0.2 preview (`v0.2.0`)

- [x] Development preview mounts at `/hedron-explorer/` when `explorer="development"` (including under `security="standard"`).
- [x] Explorer is absent when `explorer="off"` (default production posture).
- [x] `explorer="secured"` rejects anonymous requests (requires `request.state.hedron_authenticated` or supplied dependencies).
- [x] Preview lists registry routes/components and static security findings; secrets and absolute paths are not echoed as live data.

## Full Explorer coverage *(phase 0.4)*

- [x] Components, pages, actions, routes, examples, graph, source, HDN, styles, assets, HTMX, security, accessibility, packages, and settings have defined views. *(data/charts/async/cache/timing panels are stubbed for later phases)*
- [x] Preview uses the production renderer and application asset manifest.
- [x] Automatic route, target, swap, style, and asset decisions include human-readable explanations (CLI `preview`/`inspect` and Explorer inference panel).
- [x] Dependency overrides and sample data are isolated and reset between examples.

## Security and accessibility

- [x] Explorer routes are absent in production by default (`explorer="off"`).
- [x] Production opt-in requires authorization, redaction, rate limiting, and audit logs. *(secured mode)*
- [x] Arbitrary paths, modules, URLs, headers, and unregistered identifiers cannot be submitted.
- [x] Mutation simulation is disabled by default.
- [x] The interface is keyboard operable and passes declared accessibility checks.

## Exit

Phase 0.4 Explorer panels, secured controls, and inference explanations are covered by integration and unit suites.

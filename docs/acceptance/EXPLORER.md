# Component Explorer acceptance

## Phase 0.2 preview (`v0.2.0`)

- [x] Development preview mounts at `/hedron-explorer/` when `explorer="development"` (including under `security="standard"`).
- [x] Explorer is absent when `explorer="off"` (default production posture).
- [x] `explorer="secured"` rejects anonymous requests (requires `request.state.hedron_authenticated` or supplied dependencies).
- [x] Preview lists registry routes/components and static security findings; secrets and absolute paths are not echoed as live data.

## Full Explorer coverage *(phase 0.4)*

- [ ] Components, pages, actions, routes, examples, graph, source, HDN, styles, assets, HTMX, security, accessibility, data, charts, async, cache, and timing have defined views.
- [ ] Preview uses the production renderer and application asset manifest.
- [ ] Every automatic route, target, swap, renderer, style, and asset decision includes a human-readable explanation.
- [ ] Dependency overrides and sample data are isolated and reset between examples.

## Security and accessibility

- [x] Explorer routes are absent in production by default (`explorer="off"`).
- [ ] Production opt-in requires authorization, redaction, rate limiting, and audit logs. *(secured mode auth only in 0.2)*
- [ ] Arbitrary paths, modules, URLs, headers, and unregistered identifiers cannot be submitted.
- [ ] Mutation simulation is disabled by default.
- [ ] The interface is keyboard operable and passes declared accessibility checks.

## Exit

Phase 0.2 preview mounts are gated and tested. Full Explorer security exit awaits phase 0.4.

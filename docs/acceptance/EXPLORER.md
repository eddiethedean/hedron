# Component Explorer acceptance

## Coverage

- [ ] Components, pages, actions, routes, examples, graph, source, HDN, styles, assets, HTMX, security, accessibility, data, charts, async, cache, and timing have defined views.
- [ ] Preview uses the production renderer and application asset manifest.
- [ ] Every automatic route, target, swap, renderer, style, and asset decision includes a human-readable explanation.
- [ ] Dependency overrides and sample data are isolated and reset between examples.

## Security and accessibility

- [ ] Explorer routes are absent in production by default.
- [ ] Production opt-in requires authorization, redaction, rate limiting, and audit logs.
- [ ] Arbitrary paths, modules, URLs, headers, and unregistered identifiers cannot be submitted.
- [ ] Mutation simulation is disabled by default.
- [ ] The interface is keyboard operable and passes declared accessibility checks.

## Exit

Security tests confirm that no secret, cookie, authorization header, local source path, or production data mutation crosses the Explorer boundary unintentionally.


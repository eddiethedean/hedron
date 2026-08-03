# Security acceptance

## Required threat scenarios

- [ ] XSS attempts in text, attributes, URLs, CSS, JSON, raw HTML, Markdown, SVG, chart specs, and DataEditor values.
- [ ] CSRF on unsafe cookie-authenticated forms, actions, and editor mutations.
- [ ] Open redirects, unsafe URL schemes, selector/attribute injection, and GET mutation.
- [ ] Accidental public addressability and lazy-resource authorization bypass.
- [ ] Secret leakage through repr, errors, logs, traces, examples, Explorer, identities, cache keys, OpenAPI, and manifests.
- [ ] Public caching of user, tenant, locale, or permission-sensitive fragments.
- [ ] Asset traversal, symlink escape, remote fetch, MIME confusion, and undeclared executable content.
- [ ] Plugin and Explorer capability abuse, arbitrary path/module/URL access, and production exposure.
- [ ] Mass assignment and forged edits of hidden or read-only fields.

## Release controls

- [ ] Standard and strict profiles have documented headers and CSP behavior.
- [ ] CI can emit stable text, JSON, and SARIF diagnostics.
- [ ] Dependency and component-package audits run in the release pipeline.
- [ ] A maintained threat model records trust boundaries and residual risks.

## Exit

No critical or high finding remains open; accepted lower findings have owners, rationale, and target release.


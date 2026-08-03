# Scoped styles acceptance

## Compilation

- [x] Classes, compound selectors, keyframes, animation shorthands, and relative URLs are structurally rewritten.
- [ ] Full nesting / pseudo / variant suites. *(Deferred — partial coverage via keyframes + classes is enough for the 0.3 exit; expand suites later.)*
- [x] Generated identifiers are stable across machines, paths, timestamps, and import order.
- [x] Unknown `styles.name` references fail with source and suggestions.
- [x] `:global(...)`, tokens, layers, and application overrides follow documented semantics.
- [x] Traversal, symlink escape, remote fetch, missing assets, and unsafe bare `html`/`body` are rejected by policy.

## Delivery

- [x] One fingerprinted bundle styles initial and HTMX-loaded components (reference app builds and injects `/hedron-assets/` under strict CSP).
- [x] Production requires no runtime CSS compilation (`HED-BUILD-0004` on compile APIs).
- [x] Strict CSP works with external styles.
- [x] Explorer maps symbols to compiled output and reports diagnostics. *(phase 0.4 Explorer panels)*

## Exit

Repeated clean builds produce identical manifests and pass browser rendering, security, and theme tests.

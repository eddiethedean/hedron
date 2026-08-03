# Scoped styles acceptance

## Compilation

- [ ] Classes, compound selectors, pseudos, nesting, keyframes, animation shorthands, and relative URLs are structurally rewritten.
- [ ] Generated identifiers are stable across machines, paths, timestamps, and import order.
- [ ] Unknown `styles.name` references fail with source and suggestions.
- [ ] `:global(...)`, tokens, variants, layers, and application overrides follow documented semantics.
- [ ] Traversal, symlink escape, remote fetch, and unsafe inline requirements are rejected by policy.

## Delivery

- [ ] One fingerprinted bundle styles initial and HTMX-loaded components without flashes caused by missing assets.
- [ ] Production requires no runtime CSS compilation.
- [ ] Strict CSP works with external styles.
- [ ] Explorer maps authored symbols to compiled output and reports diagnostics.

## Exit

Repeated clean builds produce identical manifests and pass browser rendering, security, and theme tests.


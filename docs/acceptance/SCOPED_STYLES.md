# Scoped styles acceptance

## Compilation

- [x] Classes, compound selectors, pseudos, nesting, keyframes, animation shorthands, and relative URLs are structurally rewritten.
- [x] Generated identifiers are stable across machines, paths, timestamps, and import order.
- [x] Unknown `styles.name` references fail with source and suggestions.
- [x] `:global(...)`, tokens, variants, layers, and application overrides follow documented semantics.
- [x] Traversal, symlink escape, remote fetch, and unsafe inline requirements are rejected by policy.

## Delivery

- [x] One fingerprinted bundle styles initial and HTMX-loaded components without flashes caused by missing assets.
- [x] Production requires no runtime CSS compilation.
- [x] Strict CSP works with external styles.
- [x] Explorer maps symbols to compiled output and reports diagnostics. *(registry metadata ready; full Explorer panels remain phase 0.4)*

## Exit

Repeated clean builds produce identical manifests and pass browser rendering, security, and theme tests.

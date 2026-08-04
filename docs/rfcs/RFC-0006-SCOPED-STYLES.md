# RFC-0006: Scoped styles

**Status:** Accepted

## Design

Components may own ordinary `styles.css`. Local classes and keyframes are structurally parsed and
rewritten to stable collision-free identifiers. Python components receive typed `styles.name`
symbols; optional Jinja component calls receive rewritten class symbols through the same registry.
`:global(...)` is the explicit escape hatch.

Stable names must not depend on absolute paths, timestamps, randomness, or import order. CSS custom properties carry tokens and themes; semantic variants map to classes. Light DOM is the default.

## Delivery

The MVP emits one deduplicated fingerprinted application component stylesheet so later HTMX fragments never arrive unstyled. Assets referenced by CSS are restricted to registered roots, fingerprinted, and rewritten. Production performs no required runtime CSS compilation.

CSS is delivered externally for strict Content Security Policy compatibility. Cascade layers are ordered as reset, tokens, base, components, utilities, and overrides.

## Diagnostics

Unknown symbols, unsafe globals, path traversal, unused local selectors, duplicate symbols, missing variants, remote resources, and CSP conflicts appear in CLI and Explorer.

## Acceptance criteria

- Selector and keyframe rewriting uses an AST, not regular expressions.
- Repeated builds produce byte-equivalent names and manifests.
- HTMX-loaded components are styled without dynamic inline injection.

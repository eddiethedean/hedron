# CSS compiler implementation

## Pipeline

1. Parse CSS into an AST with source locations.
2. Discover local classes, keyframes, imports, URLs, global escapes, variables, and layer declarations.
3. Generate stable scoped identifiers from package, component, and symbol identities.
4. Rewrite selectors, animation references, and registered relative asset URLs.
5. Validate policy, variants, tokens, and browser-target configuration.
6. Emit compiled CSS, source map, symbol manifest, asset dependencies, and diagnostics.

Hashes exclude absolute paths, timestamps, import order, and randomness. Human-readable development names and compressed production names map to the same logical symbols.

## Delivery

The MVP concatenates deduplicated component CSS into one application bundle in the defined cascade-layer order. The asset pipeline fingerprints the result. Development rebuilds only affected manifests and refreshes Explorer previews.

## Guardrails

Registered roots prevent traversal. Remote fetch is disabled. Strict mode rejects inline-style requirements, remote resources, and disallowed global selectors. CSS custom properties are the dynamic theming path.

## Verification

Test nested selectors, complex pseudos, keyframes, animation shorthands, escaped identifiers, URLs, source maps, global/local boundaries, deterministic builds, and adversarial traversal. Regular expressions are not used as the rewriting engine.


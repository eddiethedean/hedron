# HDN parser and compiler implementation

## Stages

1. Lex tags, attributes, text, directives, expressions, and comments with byte and line spans.
2. Parse a lossless-enough syntax tree for formatting and diagnostics.
3. Resolve native elements, components, custom elements, props, locals, and slots.
4. Type-check expressions and component calls against model and registry schemas.
5. Validate HTML, accessibility, security, and style-symbol rules.
6. Lower to a typed render program and dependency manifest.
7. Optimize static fragments without changing source-observable semantics.

## Expression engine

The engine implements literals, property access, indexes where safely typed, boolean/comparison operators, null coalescing, string concatenation, conditions, loops, and registered pure helpers. It has no general Python evaluation. Execution is bounded and cannot access imports, reflection, filesystem, network, or process state.

## Artifacts

Compiled output includes source maps, component/style/asset dependencies, stable diagnostics, and a format version. Production rejects unsupported major versions and does not require source templates at runtime when a compiled artifact exists.

## Verification

Maintain grammar, precedence, recovery, type, escaping, security, source-map, formatter idempotence, and malicious-input suites. Fuzz the lexer/parser with bounded resources.


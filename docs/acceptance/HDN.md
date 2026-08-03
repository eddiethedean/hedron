# HDN acceptance

## Language

- [x] Grammar covers native tags, components, custom elements, fragments, props, children, slots, conditions, loops, and pure helpers.
- [x] Operator precedence and error recovery are specified by fixtures.
- [x] Arbitrary Python/JavaScript execution, imports, reflection, filesystem, and network access are impossible through the language.
- [x] Contextual escaping and `TrustedHtml` rules match Python rendering.
- [x] HTML, component, accessibility, style-symbol, and security errors include source spans.

## Tooling

- [x] Formatter is idempotent.
- [x] Source maps identify original templates.
- [x] `inspect` and `eject` preserve semantic contracts.
- [x] Production consumes versioned compiled artifacts without Node.js.
- [x] Parser/compiler fuzz tests have bounded time and memory.

## Exit

The reference application’s custom components can be implemented in either Python or HDN with equivalent observable output and diagnostics.

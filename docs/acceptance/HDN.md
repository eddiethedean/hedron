# HDN acceptance

## Language

- [ ] Grammar covers native tags, components, custom elements, fragments, props, children, slots, conditions, loops, and pure helpers.
- [ ] Operator precedence and error recovery are specified by fixtures.
- [ ] Arbitrary Python/JavaScript execution, imports, reflection, filesystem, and network access are impossible through the language.
- [ ] Contextual escaping and `TrustedHtml` rules match Python rendering.
- [ ] HTML, component, accessibility, style-symbol, and security errors include source spans.

## Tooling

- [ ] Formatter is idempotent.
- [ ] Source maps identify original templates.
- [ ] `inspect` and `eject` preserve semantic contracts.
- [ ] Production consumes versioned compiled artifacts without Node.js.
- [ ] Parser/compiler fuzz tests have bounded time and memory.

## Exit

The reference application’s custom components can be implemented in either Python or HDN with equivalent observable output and diagnostics.


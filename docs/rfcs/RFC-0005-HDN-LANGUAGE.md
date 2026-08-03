# RFC-0005: HDN language

**Status:** Accepted

## Purpose

HDN is an optional, JSX-inspired, HTML-first language for developers who need direct markup control. It is not required for onboarding and does not embed Python or JavaScript execution.

## Syntax and semantics

- Lowercase tags are native HTML elements.
- Uppercase tags resolve registered Hedron components.
- Hyphenated tags are custom elements.
- Expressions support literals, property access, safe operators, conditions, iteration, and a small registry of pure helpers.
- Children, fragments, named slots, and explicit raw HTML are supported.
- HTML uses `class` and `for`, not React DOM aliases.

Expression output is contextually escaped. Raw HTML requires `TrustedHtml`; dynamic attribute names, arbitrary imports, reflection, filesystem access, network access, and arbitrary function calls are prohibited.

## Tooling

The compiler emits an AST, typed render program, dependency manifest, style-symbol references, source map, and stable diagnostics. `hedron inspect` explains a built-in template and `hedron eject` creates a local override.

## Acceptance criteria

- The grammar, precedence, escaping contexts, slots, and diagnostics have fixtures.
- Python and HDN versions of representative components produce equivalent results.
- HDN compilation requires no Node.js runtime.


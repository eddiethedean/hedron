# RFC-0005: HDN language

**Status:** Historical — removed in 0.9

> **Historical design:** D-041 and [RFC-0031](RFC-0031-JINJA-INTEGRATION.md) replace this language
> with optional Jinja in 0.9 and remove it without a compatibility runtime. This document records
> 0.8 behavior only and does not constrain Jinja.

## Purpose

HDN is an optional, HTML-first language for developers who need direct markup control. Source
templates use the `.hdn` extension and canonical `template.hdn` filename; no alternate template
extension is discovered. HDN is not required for onboarding and does not embed Python or JavaScript
execution.

## Syntax and semantics

- Lowercase tags are native HTML elements.
- Uppercase tags resolve Hedron components. Top-level `{@import LocalName from
  "component-logical-id"}` declarations make those dependencies explicit; templates
  without declarations retain implicit tag-name lookup for compatibility.
- Hyphenated tags are custom elements.
- Expressions support literals, property access, safe operators, conditions, iteration, and a small registry of pure helpers.
- Children, fragments, named slots, and explicit raw HTML are supported.
- HTML uses `class` and `for`, not React DOM aliases.

Expression output is contextually escaped. Raw HTML requires `TrustedHtml`; dynamic
attribute names, arbitrary Python/JavaScript module imports, reflection, filesystem
access, network access, and arbitrary function calls are prohibited. Component import
declarations are inert logical-ID bindings resolved only from the host-provided component
mapping.

## Tooling

The compiler emits an AST, typed render program, dependency manifest, style-symbol references, source map, and stable diagnostics. `hedron inspect` explains a built-in template and `hedron eject` creates a local override.

## Acceptance criteria

- The grammar, precedence, escaping contexts, slots, and diagnostics have fixtures.
- Python and HDN versions of representative components produce equivalent results.
- HDN compilation requires no Node.js runtime.

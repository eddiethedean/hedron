# RFC-0023: Accessibility

**Status:** Accepted

## Commitment

Accessibility is a component contract and release requirement, not a documentation suggestion. Built-in components target WCAG 2.2 AA where applicable and use native elements before ARIA.

## Requirements

- Interactive components have accessible names, keyboard operation, visible focus, states, relationships, and error announcements.
- Forms generate labels, instructions, required state, and error associations.
- Lazy regions expose busy, fallback, error, and retry states.
- DataEditor supports keyboard navigation and does not rely only on color.
- Charts require descriptions and appropriate static or tabular fallbacks.
- Themes support contrast, reduced motion, zoom, reflow, forced colors, and touch target needs.

Compiler and Explorer diagnostics catch statically knowable problems but do not claim to prove accessibility. Components may require an explicit waiver with rationale for requirements that cannot be automated.

## Acceptance criteria

- Every built-in interactive component has a keyboard interaction specification.
- Automated semantic checks, browser axe-style tests, and manual scenarios are part of release gates.
- Accessibility metadata is available to examples, Explorer, and documentation generators.


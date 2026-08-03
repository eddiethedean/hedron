# RFC-0021: Browser runtime

**Status:** Proposed

## Boundary

Ordinary Hedron components render standard light-DOM HTML. HTMX owns requests and swaps. Web Components own interaction that must persist locally between requests, including grids, chart runtimes, editors, maps, and browser APIs.

Hedron does not ship a virtual DOM, hydration layer, synthetic event system, or global client store. First-party browser code is native ES modules and works without an application Node.js build. Optional bundling may be supported but is never required.

## Contracts

Browser modules are explicitly registered, pinned, fingerprinted, locally served, and included in the asset manifest. Custom elements declare observed attributes, properties, methods, events, accessibility behavior, and HTMX swap lifecycle needs. Light DOM is preferred when HTMX targets descendants; Shadow DOM is used only for intentionally isolated widgets.

Inline event handlers and arbitrary executable callbacks are prohibited by default. Typed custom events may bridge to HTMX through registered payload contracts.

## Acceptance criteria

- Components operate under a strict Content Security Policy.
- Repeated HTMX swaps initialize and dispose browser behavior without leaks or duplicate listeners.
- Browser packages declare all JavaScript, CSS, fonts, workers, and remote resources for audit.


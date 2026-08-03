# Accessibility acceptance

## Phase 0.1 (`v0.1.0`) built-in subset

- [x] Native semantic elements are used before ARIA for landmarks and structure.
- [x] Controls expose accessible names (`Button`, `IconButton` aria-label).
- [x] Forms associate labels (`for`/`id`), help, required/`aria-required`, errors/`aria-invalid`/`aria-describedby`.
- [ ] Dialog-like, tab, expander, toast, progress, and status patterns. *(later built-ins)*
- [ ] Lazy and error regions expose busy and retry states. *(phase 0.2)*
- [ ] Data tables, DataEditor, charts, code, JSON, uploads, and downloads. *(phases 0.5–0.6)*

## Visual and responsive

- [ ] Reference themes meet WCAG 2.2 AA contrast where applicable. *(phase 0.3)*
- [ ] Zoom, reflow, reduced motion, forced colors, touch targets, and color-independent meaning are tested.
- [ ] HTMX swaps preserve logical focus and announcements. *(phase 0.2)*

## Verification

- [x] Static markup checks for the 0.1 built-in catalog.
- [ ] Browser axe-style checks, keyboard scenarios, and screen-reader spot checks. *(phase 0.2+)*
- [ ] Explorer reports known issues without claiming automated proof of accessibility. *(phase 0.4)*
- [ ] Waivers contain rationale, affected users, and remediation plan.

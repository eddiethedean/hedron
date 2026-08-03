# Accessibility acceptance

## Phase 0.1 (`v0.1.0`) built-in subset

- [x] Native semantic elements are used before ARIA for landmarks and structure.
- [x] Controls expose accessible names (`Button`, `IconButton` aria-label).
- [x] Forms associate labels (`for`/`id`), help, required/`aria-required`, errors/`aria-invalid`/`aria-describedby`.
- [x] Dialog-like, tab, expander, toast, progress, and status patterns. *(phase 0.5 utility smoke markup)*
- [x] Lazy and error regions expose busy and retry affordances (`aria-busy` / `aria-live` on `Lazy`/`Loading`; `role="alert"` and retry controls on `ErrorState`). *(phase 0.2 markup)*
- [x] Phase 0.5 utility/table smoke: DataTable captions/`scope`, Metric/Progress/Status/Toast/Expander/Tabs/ColorMode/Sidebar accessible names and live regions. *(unit/a11y smoke; not full AT coverage)*
- [ ] Charts, richer DataEditor keyboard/AT corpus, uploads/downloads beyond markup contracts. *(phases 0.5 hardening / 0.6)*

## Visual and responsive

- [x] Reference themes meet WCAG 2.2 AA contrast where applicable. *(phase 0.3 default theme tokens)*
- [ ] Zoom, reflow, reduced motion, forced colors, touch targets, and color-independent meaning are tested.
- [ ] HTMX swaps preserve logical focus and announcements. *(Deferred: browser/keyboard suite; phase 0.4+)*

## Verification

- [x] Static markup checks for the 0.1 built-in catalog.
- [x] Explorer reports known issues without claiming automated proof of accessibility. *(phase 0.4)*
- [x] Browser axe-style hooks exist via `hedron[browser]` (advisory; optional dependency). *(phase 0.4)*
- [ ] Waivers contain rationale, affected users, and remediation plan.

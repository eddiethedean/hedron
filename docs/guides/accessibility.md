# Accessibility

Hedron aims for an accessible **HTML baseline**, not an automatic WCAG certification.
Authors remain responsible for labels, focus, and interaction patterns in their apps.

## What Hedron provides

- Semantic built-ins (landmarks, forms, tables, dialogs) that emit ordinary HTML
- Stable identities for targets and tests without encoding secrets
- Documented component contracts in the [Components](../components/index.md) catalog
- Optional browser helpers via `hedron[browser]` for Playwright evidence

## Author checklist

1. Every interactive control has an accessible name (`Label`, `aria-label`, or visible text).
2. Forms associate labels with inputs (`FormField` / `Label` + matching `name`).
3. Dialogs and expanders restore focus; do not trap keyboard users without an exit.
4. Status and errors use polite live regions where appropriate (`role="status"`, alerts).
5. Do not rely on color alone for state; pair with text or icons that have names.
6. Test critical flows with keyboard-only navigation and one screen reader pass.

## What Hedron does not claim

- Automatic WCAG conformance or legal certification
- That every third-party chart/grid Web Component is accessible out of the box
- That Alpha chart surfaces meet the same bar as core built-ins

## Research and RFCs

Maintainer research and RFC-0023 live in the repository (see
[For maintainers](maintainers.md)). Adopters should treat this guide as the day-one
checklist.

## See also

[Security](security.md) · [Testing](testing.md) · [Components](../components/index.md)

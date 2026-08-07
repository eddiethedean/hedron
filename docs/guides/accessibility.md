# Accessibility

Hedron aims for an accessible **HTML baseline**, not automatic WCAG / legal / VPAT
certification. Authors remain responsible for labels, focus, and interaction patterns.

**0.19** ships accessibility engineering APIs (`hedron_core.a11y`), Explorer review,
progressive-enhancement forms, landmarks, and automated Playwright/axe evidence.
Human screen-reader evaluation is **Deferred → 0.21**.

Narrative: [What's new in 0.19](whats-new-0.19.md) · API: [A11Y](../api/A11Y.md).

## What Hedron provides

- Semantic built-ins (landmarks, forms, tables, dialogs) that emit ordinary HTML
- Versioned standards profile and machine-readable `AccessibilityContract` catalog
- Explorer accessibility workspace (`/hedron-explorer/a11y` with `hedron[dev]`)
- Progressive-enhancement POST (no-JS full page / redirect alongside HTMX)
- Allowlisted `Page(scripts=[SafeUrl…])` for same-origin PE scripts
- `AccessibilityScenario`, axe → SARIF helpers, and automated three-engine AT matrix
- Stable identities for targets and tests without encoding secrets
- Documented component contracts in the [Components](../components/index.md) catalog
- Optional browser helpers via `hedron[browser]` for Playwright evidence

## `hedron_core.a11y` (0.19)

Import from `hedron_core.a11y` (re-exported where noted). Full contract:
[A11Y API](../api/A11Y.md).

| Surface | Role |
|---|---|
| `ACCESSIBILITY_PROFILE` / `AccessibilityProfile` | Pinned WCAG 2.2 A/AA + WAI-ARIA 1.2 baseline (`PROFILE-019`) |
| `ClaimBoundary` | Explicit non-goals (no auto WCAG / legal / certification / VPAT) |
| `AccessibilityContract` / catalog | Leaf or package obligations — **never** implies app conformance |
| `AccessibilityScenario` | Structured evidence steps; empty scans are **not** “accessible” |
| `EvidenceInventory` / `Waiver` / `AccessibilityStatement` | Governance (`GOVERN-019`); statements need human `approved_by` |
| Surface helpers | Structure validation, media tracks, cognitive prefs, target spacing |

```python
from hedron_core.a11y import ACCESSIBILITY_PROFILE, AccessibilityContractCatalog

assert ACCESSIBILITY_PROFILE.claim_boundaries.forbids_auto_wcag_conformance
catalog = AccessibilityContractCatalog()
catalog.ensure_registry()
```

### Claim boundaries

Hedron **refuses** automatic conformance, legal compliance, certification, and VPAT/ACR
claims (`refuse_auto_conformance_claim`). Component contracts record obligations and
limitations; composition can still leave unmet criteria. Empty axe scans never summarize
as accessible.

## Explorer `/a11y` workspace

With `explorer="development"` or `"secured"` and `hedron[dev]`, open
`/hedron-explorer/a11y` for:

- Standards profile summary
- Component contract table (registry stubs + curated reviewed contracts)
- Review-mode checklist (contrast, target spacing, zoom/reflow, reduced motion, …)
- ATAG authoring notes beside component inspect metadata

See [Explorer API](../api/EXPLORER.md).

## Progressive enhancement, landmarks, and `Page(scripts=)`

| Gate | What to do |
|---|---|
| `PE-019` | Critical forms/mutations succeed **without** `HX-Request` — full `Page` or redirect. HTMX is optional enhancement. |
| `LANDMARK-019` | Use typed `Header` / `Main` / `Nav` / `Aside` / `Footer` / `Section` with allowlisted safe attrs. |
| `SCRIPT-019` | Attach same-origin PE scripts via `Page(scripts=[SafeUrl.parse(..., purpose=UrlPurpose.ASSET)])` — no free-form `<script>` in the tree. |

Details: [Forms and actions](forms-and-actions.md) · [Page](../components/page.md) ·
[Landmarks](../components/landmarks.md).

## AT matrix (`AT-019`) vs human AT

**0.19 Verified:** automated three-engine Playwright matrix (Chromium, Firefox, WebKit)
covering keyboard, zoom/reflow, reduced motion, forced colors, plus pinned axe/ACT
provenance after representative dynamic states (`hedron[browser]`).

**Deferred → 0.21:** compensated human screen-reader / disabled-participant evaluation.
Do not market automated evidence as human AT sign-off.

## Author checklist

1. Every interactive control has an accessible name (`Label`, `aria-label`, or visible text).
2. Forms associate labels with inputs (`FormField` / `Label` + matching `name`).
3. Dialogs and expanders restore focus; do not trap keyboard users without an exit.
4. Status and errors use polite live regions where appropriate (`role="status"`, alerts).
5. Do not rely on color alone for state; pair with text or icons that have names.
6. Prefer no-JS POST success for critical mutations; enhance with HTMX where useful.
7. Test critical flows with keyboard-only navigation; plan a screen-reader pass (0.21 owns
   compensated AT evidence).

## What Hedron does not claim

- Automatic WCAG conformance or legal certification
- That every third-party chart/grid Web Component is accessible out of the box
- That Alpha chart surfaces meet the same bar as core built-ins
- That Playwright/axe results replace human AT evaluation

## Research and RFCs

Maintainer RFCs (GitHub; excluded from Read the Docs builds):

- [RFC-0023](https://github.com/eddiethedean/hedron/blob/main/docs/rfcs/RFC-0023-ACCESSIBILITY.md) (umbrella)
- [RFC-0051](https://github.com/eddiethedean/hedron/blob/main/docs/rfcs/RFC-0051-ACCESSIBILITY-CONTRACT.md) AccessibilityContract
- [RFC-0052](https://github.com/eddiethedean/hedron/blob/main/docs/rfcs/RFC-0052-A11Y-EXPLORER-SCENARIO.md) Explorer / AccessibilityScenario
- [RFC-0053](https://github.com/eddiethedean/hedron/blob/main/docs/rfcs/RFC-0053-PROGRESSIVE-ENHANCEMENT.md) PE / landmarks / Page scripts
- [RFC-0054](https://github.com/eddiethedean/hedron/blob/main/docs/rfcs/RFC-0054-ATAG-AUTHORING.md) ATAG authoring
- [RFC-0055](https://github.com/eddiethedean/hedron/blob/main/docs/rfcs/RFC-0055-A11Y-GOVERNANCE.md) Governance / AT matrix

Adopters should treat this guide as the day-one checklist. Maintainers:
[For maintainers](maintainers.md).

## See also

[A11Y API](../api/A11Y.md) · [What's new in 0.19](whats-new-0.19.md) ·
[Security](security.md) · [Testing](testing.md) · [Components](../components/index.md)

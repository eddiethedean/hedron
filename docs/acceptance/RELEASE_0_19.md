# Hedron `v0.19` accessibility engineering and inclusive authoring acceptance

Phase 0.19 delivers versioned accessibility contracts, ATAG-oriented authoring assistance,
Explorer accessibility review, scenario/ACT-axe evidence, AT matrix and governance outputs,
and progressive-enhancement / landmark / Page-script work — without automatic WCAG, legal,
certification, or ACR/VPAT claims. Evidence is indexed by
[`release-gate-0.19.toml`](release-gate-0.19.toml).
**Zero Deferred:** every 0.19-owned gate row must be Verified at cut.

Owning RFCs: [RFC-0023](../rfcs/RFC-0023-ACCESSIBILITY.md) (umbrella),
[RFC-0051](../rfcs/RFC-0051-ACCESSIBILITY-CONTRACT.md),
[RFC-0052](../rfcs/RFC-0052-A11Y-EXPLORER-SCENARIO.md),
[RFC-0053](../rfcs/RFC-0053-PROGRESSIVE-ENHANCEMENT.md),
[RFC-0054](../rfcs/RFC-0054-ATAG-AUTHORING.md),
[RFC-0055](../rfcs/RFC-0055-A11Y-GOVERNANCE.md). Decision: [D-050](../DECISIONS.md).

Issues [#8](https://github.com/eddiethedean/hedron/issues/8),
[#27](https://github.com/eddiethedean/hedron/issues/27),
[#31](https://github.com/eddiethedean/hedron/issues/31), and
[#39](https://github.com/eddiethedean/hedron/issues/39) remain normative for
`PE-019` / `LANDMARK-019` / `SCRIPT-019`.

## Spec packet

- [x] ROADMAP §0.19 scope accepted; accessibility research refreshed (dated baselines).
- [x] RFCs 0051–0055 Accepted; RFC-0023 umbrella current.
- [x] Entry gate: 0.18 evidence remains closed; 0.19 gate TOML owns Planned→Verified rows only.
- [x] Gate checker recognizes `0.19` (`python scripts/check_release_gate.py 0.19.0 --allow-planned`).

## Profile, contracts, interaction

- [x] Versioned WCAG 2.2 A/AA + WAI-ARIA 1.2 profile and claim boundaries. *(`PROFILE-019`)*
- [x] `AccessibilityContract` catalog coverage. *(`CONTRACT-019`)*
- [x] WCAG 2.2 interaction/conformance cases. *(`INTERACT-019`)*

## Authoring and Explorer

- [x] ATAG-oriented authoring assistance and metadata preservation. *(`ATAG-019`)*
- [x] Explorer accessibility review workspace. *(`EXPLORER-019`)*

## Testing, AT, media, cognitive, i18n

- [x] `AccessibilityScenario`, tree snapshots, ACT/axe provenance. *(`TEST-019`)*
- [x] Automated three-engine Playwright/axe AT matrix (human AT Deferred → 0.21). *(`AT-019`)*
- [x] Media and complex-content alternatives. *(`MEDIA-019`)*
- [x] Cognitive/personalization helpers. *(`COG-019`)*
- [x] Language/direction/structure validation. *(`I18N-019`)*

## Governance and progressive enhancement

- [x] Evidence inventory, statement template, waiver governance. *(`GOVERN-019`)*
- [x] Progressive-enhancement forms/mutations (#8). *(`PE-019`)*
- [x] Landmark attrs and real types (#27, #31). *(`LANDMARK-019`)*
- [x] Allowlisted `Page` PE scripts (#39). *(`SCRIPT-019`)*

## Packaging

- [x] Coordinated package verify (`scripts/verify_pkg_19.py`). *(`PKG-019`)*

## Exit

- [x] Full regression suite. *(`REGRESS-019`)*

**Exit met** — coordinated `0.19.0` (**Published** as `v0.19.0`); every 0.19 gate row Verified.

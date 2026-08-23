# Phase 0.60 acceptance plan — custom theme platform and styling completion

**State:** Implemented and verified in-tree as `v0.60.0`; PyPI publication remains deferred
**Baseline:** Published/Verified in-tree and PyPI `v0.59.0`
**Target:** `v0.60.0`
**Authority:** RFC-0089 / D-108 / `theme-platform-*-060.toml`

## Outcome

A Hedron author can create a canonical ThemeSpec from a reviewed built-in, typed modern color,
finite design groups, or explicit semantic palette; compose bounded ThemePatches; validate it
against registry-derived component contracts and a truthful coverage profile; package and register
it without executable theme code; reproduce and verify its fingerprint; run the third-party
conformance kit; preview/diff/explain it; and offer a server-authoritative, accessible, persisted
theme picker with an optional CSP-safe no-flash path.

All nine 0.60 styling issues close through behavior evidence. Existing 0.59 themes, hex brand
inputs, recipes, scopes, public markers/tokens, component CSS, and host behavior remain compatible.

## Required issue closure

| Issue | Phase result | Closing gates |
|---|---|---|
| [#627](https://github.com/eddiethedean/hedron/issues/627) | Brand name/subtitle stack and constrain without application CSS | `BRAND-060`, `A11Y-060`, `VISUAL-060`, `COMPAT-060` |
| [#628](https://github.com/eddiethedean/hedron/issues/628) | ToastHost owns placement/layout and a coherent announcement/error-host strategy | `FEEDBACK-060`, `A11Y-060`, `SECURITY-060`, `COMPAT-060` |
| [#629](https://github.com/eddiethedean/hedron/issues/629) | ConnectorFlow supports bounded themed canvas presentation | `WORKFLOW-060`, `A11Y-MODE-060`, `VISUAL-060` |
| [#630](https://github.com/eddiethedean/hedron/issues/630) | ScrollRegion bounds semantic logs/lists without changing child semantics | `SCROLL-060`, `A11Y-060`, `VISUAL-060` |
| [#631](https://github.com/eddiethedean/hedron/issues/631) | Explicit scoped recipe defaults preserve deterministic precedence and fragments | `SCOPE-060`, `RECIPE-060`, `COMPAT-060` |
| [#632](https://github.com/eddiethedean/hedron/issues/632) | Custom presentation-only recipe families validate and package deterministically | `RECIPE-060`, `PACKAGE-060`, `SECURITY-060` |
| [#633](https://github.com/eddiethedean/hedron/issues/633) | Modern absolute color inputs compile with sRGB fallback and palette-v2 provenance | `RECONCILE-060`, `COLOR-060`, `PALETTE-060`, `COMPAT-060` |
| [#634](https://github.com/eddiethedean/hedron/issues/634) | Themes declare reviewed forced-color/more-contrast semantic mappings | `A11Y-MODE-060`, `VALIDATE-060`, `A11Y-060` |
| [#635](https://github.com/eddiethedean/hedron/issues/635) | Registered allowlisted themes are selectable, persistable, and no-flash | `PREFERENCE-060`, `SECURITY-060`, `A11Y-060`, `COMPAT-060` |

Issue closure alone is not evidence. A gate cannot become Verified until the issue's acceptance
criteria, the relevant source fixture, and the phase compatibility matrix all pass.

## Verified release gates

| Gate | Required evidence |
|---|---|
| `CONTRACT-060` | Exact APIs, component-contract/profile map, schemas, diagnostics, issue mapping, package dispositions, browser floors, budgets, and capped design review policy |
| `RECONCILE-060` | Executable mapping of 0.59 styling claims to runtime behavior, with every mismatch owned and regression-protected |
| `COLOR-060` | Safe absolute CSS Color 4 parser/model, deterministic conversion/gamut mapping/serialization, fuzzing, and legacy hex parity |
| `PALETTE-060` | Palette-v2 light/dark generation, sRGB/wide-gamut output, contrast/focus adjustment, provenance, build/browser agreement |
| `THEME-060` | Canonical immutable ThemeSpec, ThemeBuilder facade, alias graph, bounded ThemePatch composition, provenance, reproducible fingerprints, Theme/DesignSystem bridge |
| `VALIDATE-060` | Registry-derived component contracts, truthful coverage profiles, semantic relationships, categorical diagnostics/remediation, modes, states, assets, fallbacks, compatibility |
| `PACKAGE-060` | Data-only deterministic ThemeSpec/ThemePatch package, profiles/fingerprints, hashes/licenses/migrations/compatibility, registry lifecycle, clean install/upgrade/uninstall |
| `A11Y-MODE-060` | Forced-colors/more-contrast authoring, system-color policy, state coverage, contradictions, feature-off fallback |
| `RECIPE-060` | Extensible finite presentation-only families, per-component bindings, inheritance, registration, package and invalid cases |
| `SCOPE-060` | Explicit-value tracking, StyleContext precedence, nesting, fragments/OOB hosts, static impact explanation, no mutation |
| `PREFERENCE-060` | ThemePreference/ThemePicker, allowlisting, persistence boundaries, server markers, no-JS/HTMX/history/no-flash behavior |
| `BRAND-060` | Name/subtitle layout, overflow/density tokens, name-only compatibility, narrow/RTL/zoom/forced-color/print fixture |
| `FEEDBACK-060` | ToastHost placement/safe areas/stack/width/OOB semantics, announcement ownership, error-host disposition |
| `WORKFLOW-060` | ConnectorFlow canvas appearance/background/density/overflow/min-size with decorative/fallback/accessibility behavior |
| `SCROLL-060` | ScrollRegion axes/sizes/naming/affordance, child semantics, focus/keyboard, print, RTL, zoom, long-content behavior |
| `CATALOG-060` | No more than three reviewed additions, default/aurora compatibility, complete fleet/state/mode/assets/licenses coverage, platform-before-breadth review |
| `TOOLING-060` | Shared CLI init/check/preview/diff/package/explain/conform, CI/SARIF, no-overwrite starter, source-aware candidate remediation, formatting-only fixes |
| `EXPLORER-060` | Read-only Theme Lab with side-by-side modes, token/state and spec/patch diffs, gamut/fallback warnings, keyboard/focus/zoom exercises and report export |
| `CONFORMANCE-060` | Generated declared-profile zero-CSS fixture, state/mode matrix, portable JSON and human artifacts, matching registry inventory and fingerprint digests |
| `DOCS-060` | Complete authoring ladder, APIs, accessibility limits, packages/preferences, lifecycle warnings/migrations, conformance, upgrade and advanced CSS paths |
| `VISUAL-060` | Reviewed three-engine DOM/computed-style/pixel matrix for every built-in and representative custom theme |
| `A11Y-060` | Keyboard/focus/announcements/reflow/zoom/content/direction/media/print/no-JS and bounded manual review evidence |
| `SECURITY-060` | Parser/manifest/package/asset/preference/recipe fuzzing, CSP, traversal/injection/conflict/redaction/resource budgets |
| `PERF-060` | Default/per-theme CSS, optional JS, asset requests, build/validation, style/layout, and package-size budgets |
| `COMPAT-060` | Both 0.59 sources, public API/DOM/marker/token/theme/recipe/CSS/schema/package/default behavior and rollback |
| `REGRESS-060` | Full fleet plus closed 0.57–0.59 styling contracts and corrected evidence remain green |
| `PKG-060` | Clean wheels, pure-Python Supported path, lazy assets/deps, licenses, exports, metadata, reproducible cut rehearsal |

## Evidence quality rules

- String or marker presence cannot alone verify layout, color, fallback, announcement, no-flash,
  focus, overflow, or visual claims.
- Each such gate includes DOM plus computed-style/behavior facts and reviewed browser artifacts.
- Visual snapshots need semantic assertions so a stable broken screenshot cannot pass.
- Progressive features run feature-on and feature-off; accessibility preferences run active and
  base fallbacks.
- Validation reports used as evidence are regenerated during the gate, not trusted as static pass
  labels.
- Waivers name reason, owner, scope, expiry, and affected claims; Required failures cannot be waived
  at the cut.
- Validation remains categorical: no aggregate score may hide a critical failure, and suggested
  color/accessibility changes require explicit author choice.

## Stage 1 entry (satisfied)

Runtime work began after D-108 was accepted, the exact contract, component-contract/
profile map, and capped theme design brief are reviewed, the 0.59 reconciliation probe is recorded,
#627–#635 carry the 0.60 milestone and backlinks, browser floors and validation matrix are locked,
explicit-value, package-security, and fingerprint-reproducibility prototypes pass, and all numeric
budgets have reproducible baselines.

## Exit

All 27 gates are Verified with zero Deferred among Required rows; #627–#635 are closed from
evidence; no relevant styling issue is unowned; both 0.59 upgrades pass; the built-in catalog and
representative custom packages pass their claimed profiles and conformance fixtures; clean wheels
and docs publish together;
and claims remain bounded by actual browser/manual evidence and open #86 human-AT limits.

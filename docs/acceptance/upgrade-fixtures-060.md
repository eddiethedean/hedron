# Phase 0.60 upgrade fixtures

Run every fixture from both the PyPI `v0.59.0` environment and the tagged/in-tree `v0.59.0`
baseline, then against the 0.60 candidate. Record Python API, rendered DOM, public markers, emitted
CSS, computed-style facts, validation reports, package manifests, diagnostics, and browser behavior.

## Existing behavior

1. Render built-in `default` and `aurora` pages in system/light/dark modes.
2. Compile representative hex brand seeds, including adjusted white/black cases.
3. Construct explicit `Theme`, `DesignSystem.from_theme`, built-in/custom `StyleRecipe`,
   `DesignSystem.apply`, and existing theme/mode/density/variant `StyleScope` calls.
4. Render existing Brand name-only and subtitle calls, Toast/ToastHost OOB updates,
   ConnectorFlow/ProcessFlow, tables with responsive scrolling, and ColorModeToggle.
5. Build component `styles.css` through manifest v1/v2 readers and `default_styles=False` pages.
6. Confirm current public classes, markers, theme names, token aliases, IDs, DOM order, forms,
   landmarks, and application override authority.

## New 0.60 paths

1. Parse equivalent hex/RGB/HSL/HWB/Lab/LCH/OKLab/OKLCH colors and compare normalized palette-v2
   output, fallback order, contrast, adjustments, and build/browser agreement.
2. Build equivalent themes through canonical ThemeSpec, the ThemeBuilder facade, and explicit
   Theme; compare resolved token graphs, validation provenance, and deterministic fingerprints.
3. Compose ordered valid and invalid ThemePatches; prove base-fingerprint checks, layer provenance,
   full revalidation, cycle detection, and rejection of arbitrary CSS or behavior.
4. Derive component coverage from the registry and validate complete, limited-profile, incomplete,
   contradictory, unsafe, out-of-gamut, inaccessible, and waived themes with deterministic
   relationship diagnostics and truthful profile claims.
5. Package/register/load/diff/uninstall a local theme package with specs, patches, profiles,
   fingerprints, fonts/assets/hashes/licenses/migrations; reject traversal, remote resources,
   conflicts, incompatible versions, tampering, stale conformance reports, and hooks.
6. Register a safe custom presentation family; reject behavior/state fields, bad values, cycles,
   incompatible component bindings, late registration, and package conflicts.
7. Apply nested StyleContext defaults and prove explicit component precedence, fragment inheritance,
   detached-host binding, static explanation, and no object mutation.
8. Resolve and submit ThemePicker through no-JS and HTMX paths; test valid/invalid/stale/unauthorized
   preferences, server-first paint, optional boot, CSP, history, fragments, dialogs/toasts, and
   multi-tab behavior.
9. Render #627–#630 fixtures across narrow/zoom/RTL/forced-color/contrast/print/reduced-motion and
   assert DOM plus computed layout/behavior rather than marker presence only.
10. Run the third-party conformance kit for each profile and prove portable reports, generated
    zero-CSS fixtures, inventory/fingerprint matching, and strict/compatibility lifecycle behavior.
11. Build and validate every reviewed built-in theme across the whole component/state matrix.

## Rollback

Applications can remove ThemeSpec/ThemeBuilder/ThemePatch/package/context/picker usage and retain
direct 0.59 `Theme`, `DesignSystem`, explicit recipes/props, color-mode form, and component CSS. New
data markers and package/report schemas are additive. Rollback never requires deleting application
data or changing routes, sessions, authorization, or preference storage.

## Pass rule

No undocumented API/DOM/token/theme/recipe/asset/default change; all intentional visual deltas have
reviewed before/after plus semantic and accessibility confirmation; both sources agree; unsafe or
invalid inputs fail closed; and every new path has a usable no-feature/rollback path.

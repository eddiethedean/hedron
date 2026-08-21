# Upgrade fixtures for phase 0.59

**Runtime source:** Published/Verified in-tree `v0.57.0`  
**Contract source:** D-102 / RFC-0085 (`v0.58.0` implementation pending)  
**Required Stage 1 source:** final Published/Verified in-tree `v0.58.0`  
**Target:** `v0.59.0`  
**Authority:** D-103 / D-104 / RFC-0086

D-104 is an early conditional Stage 0 refine. Before Stage 1, replace or supplement these fixtures
with the final 0.58 source/output corpus and record the predecessor audit in
`styling-tracking-059.toml`. Any material seam drift requires an accepted D-104 amendment before
runtime work.

Existing string theme selection, `Theme`, built-in themes, `Theme.extend`, `compile_palette`,
registration, semantic appearance props, `class_`, `StyleSymbols`, component `styles.css`, style
contracts, compiler output, cascade layers, `default_styles=False`, theme checks, and zero-CSS
checks retain behavior.

Locked fixture groups:

1. `Hedron(theme="default"|"aurora"|None)` before/after constructor widening.
2. Default and aurora `Theme` values, emitted CSS, manifest entries, and registered metadata.
3. A custom `default_theme().extend(...)` app imported with `DesignSystem.from_theme` and emitted
   without semantic/CSS drift when no design choices are added.
4. The current `examples/chrome-zero-css` theme, first represented explicitly and then by the
   branded design facade, with documented intentional deltas only.
5. Explicit component appearance props compared with equivalent `DesignSystem.apply` recipes.
6. Explicit theme/density markers compared with equivalent `StyleScope` output.
7. Existing scoped component CSS, `StyleSymbols`, public parts/tokens, source maps, and asset URLs.
8. Existing `theme check` and `style check --zero-app-css` CLI behavior after additive subcommands.
9. Final 0.58 minimal/CRUD/dashboard/task/auth/upload generated surfaces before and after semantic
   recipe-role inheritance, proving route/effect/security/output ownership is unchanged.
10. Whole/per-surface 0.58 ejection composed with whole/group/recipe/component 0.59 ejection.
11. Flask/Django/Jinja/elements/data/charts/maps/extras compiled-theme/marker consumption without
   false facade parity.
12. Optional package absence and rollback to explicit styling with no hidden import or asset cost.

No application is opted into `DesignSystem`, recipes, or scopes automatically. Existing emitted
CSS hashes stay unchanged unless the application explicitly selects a generated design or the
accepted fixture records an intentional first-party correction.


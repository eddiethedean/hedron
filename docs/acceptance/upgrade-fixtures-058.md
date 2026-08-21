# Upgrade fixtures for phase 0.58

**Source:** Published/Verified in-tree `v0.57.0`  
**Target:** `v0.58.0`  
**Authority:** D-101 / D-102 / D-105 / RFC-0085

Existing pages, commands, FormBody, handles, effects, features, DataWorkspace overrides, jobs,
auth, uploads, and presentation retain behavior. No app is opted into a facade or rewritten.
`FeatureOverrides` and surface source maps are additive. Flask/Django gain no false decorator
parity, and feature inclusion never implies MCP, Gradio, browser, or other protocol exposure.

Fixtures compare explicit and facade forms for page/screen, command/form_command, DataWorkspace,
JobBackend/Poll/TaskFlow, typed dashboard filters, session/upload helpers, and whole/per-surface
ejection. Optional-package absence must preserve clean imports, startup, explanation, and explicit
APIs.

The same source baseline also locks existing styling behavior: string theme selection, `Theme`,
built-in themes, `Theme.extend`, `compile_palette`, registration, semantic appearance props,
`class_`, `StyleSymbols`, component `styles.css`, style contracts, compiler output, cascade layers,
`default_styles=False`, theme checks, and zero-application-CSS checks. No application is opted into
`DesignSystem`, recipes, or scopes automatically.

Additional unified fixture groups compare:

1. `Hedron(theme="default"|"aurora"|None)` before and after accepting `Theme` and `DesignSystem`.
2. Built-in theme values, emitted CSS, manifests, and registered metadata.
3. `default_theme().extend(...)` with `DesignSystem.from_theme`, requiring no semantic or CSS drift
   when no higher-level choices are added.
4. The current chrome-zero-CSS theme and its branded equivalent, with only recorded intentional
   deltas.
5. Explicit appearance props versus equivalent `DesignSystem.apply` recipes.
6. Explicit theme/density markers versus equivalent `StyleScope` output.
7. Existing scoped CSS, `StyleSymbols`, public parts/tokens, source maps, and asset URLs.
8. Existing theme/style checks after additive design-system commands.
9. Every generated screen/form/workspace/dashboard/task/auth/upload surface before and after
   built-in semantic recipe roles, proving that routes, effects, authorization, state, DOM order,
   and accessible names are unchanged.
10. Whole/per-surface feature ejection composed with whole/group/recipe/component styling
    ejection, including both preserved recipe references and fully resolved explicit-prop output.
11. Flask/Django/Jinja/elements/data/charts/maps/extras compiled-theme and marker consumption
    without false facade parity.
12. Optional-package absence and rollback to explicit styling with no hidden import, network, or
    asset cost.

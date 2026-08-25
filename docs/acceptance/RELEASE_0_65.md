# Release acceptance — phase 0.65 integrated styling platform

Status: **Release ready for v0.65.0**. The implementation and evidence commands pass against the
current `v0.64.1` baseline, and the coordinated package metadata is cut to `v0.65.0`.

- RFC: [RFC-0092](../rfcs/RFC-0092-INTEGRATED-STYLING-PLATFORM.md)
- Implementation: [APPLICATION_STYLING_065](../implementation/APPLICATION_STYLING_065.md)
- Execution: [EXECUTION_0_65](../implementation/EXECUTION_0_65.md)
- Refined scope: [application-styling-scope-065](application-styling-scope-065.md)
- Gate index: [release-gate-0.65.toml](release-gate-0.65.toml)
- Contract: [application-styling-contract-065.toml](application-styling-contract-065.toml)
- Inventory: [application-styling-inventory-065.toml](application-styling-inventory-065.toml)

## Boundary

The cut must integrate all four currently open styling issues, with the exact slices defined by the
[refined scope](application-styling-scope-065.md):

| Issue | Required disposition | Gate |
|---|---|---|
| [#690](https://github.com/eddiethedean/hedron/issues/690) | named motion recipes with reduced-motion fallbacks | `MOTION-065` |
| [#693](https://github.com/eddiethedean/hedron/issues/693) | bounded public component-part/state recipe hooks | `HOOKS-065`, `RECIPE-065` |
| [#694](https://github.com/eddiethedean/hedron/issues/694) | semantic data-view/table chrome tokens | `DATA-065` |
| [#698](https://github.com/eddiethedean/hedron/issues/698) | native form-control appearance/state contract | `CONTROLS-065` |
| [#712](https://github.com/eddiethedean/hedron/issues/712) | document-level ambient canvas and composable decorative layers | `PRESENT-065`, `A11Y-065` |
| [#713](https://github.com/eddiethedean/hedron/issues/713) | bounded AppShell chrome layout recipes | `PRESENT-065`, `REGRESS-065` |
| [#714](https://github.com/eddiethedean/hedron/issues/714) | authoritative presentation-token consumption in built-in bundles | `TOKEN-065`, `PRESENT-065` |
| [#715](https://github.com/eddiethedean/hedron/issues/715) | bounded maximum and between-range presentation conditions | `RECIPE-065`, `A11Y-065` |

The cut also requires first-class local application CSS registration, the explicit application
cascade layer, namespaced theme tokens, stable public hooks, deterministic style diagnostics, and
provenance-preserving ejection. Broader focus, navigation, overlay, layout, typography, media,
icon, visualization, print, RTL, and user-preference coverage must be delivered or explicitly
marked Progressive/Deferred with a fallback in the inventory.

## Planned gates

All rows begin `Planned`. A gate becomes `Verified` only with retained command output and artifacts;
“implemented” or “browser looked good” is not sufficient.

| Gate | Evidence |
|---|---|
| `CONTRACT-065` | versioned schemas, precedence, compatibility, and non-goals |
| `ASSET-065` | local stylesheet asset graph, fingerprint, CSP, HTMX/head, no-JS |
| `LAYER-065` | deterministic layer order and cascade explanation |
| `TOKEN-065` | namespaced token/theme/provenance and collision fixtures |
| `HOOKS-065` | public component/part/state manifest and stability fixtures |
| `RECIPE-065` | bounded recipe/property allowlist and explicit state ownership |
| `CSS-065` | scoped/global policy, unsafe syntax rejection, source maps |
| `INSPECT-065` | explain/inspect/check deterministic diagnostics |
| `EJECT-065` | ejection, diff/update, drift, and rollback evidence |
| `MOTION-065` | motion recipes and reduced-motion/print fallbacks |
| `CONTROLS-065` | native controls appearance, focus, invalid, disabled, and browser fallback |
| `DATA-065` | table/data-view semantic chrome and state matrix |
| `PRESENT-065` | cross-cutting fallback matrix on every touched Required surface; broader verticals are inventory dispositions |
| `A11Y-065` | keyboard, focus, contrast, forced-colors, AT, and no-JS evidence |
| `SECURITY-065` | CSP, unsafe CSS, asset provenance, package trust, and redaction |
| `PERF-065` | manifest/compile/request/layout budgets with reject-not-slice behavior |
| `FLEET-065` | flagship, starters, packages, adapters, and examples |
| `UPGRADE-065` | 0.64.0/0.64.1 compatibility, migration, and rollback fixtures |
| `REGRESS-065` | full unit/browser/static/docs regression suite |
| `DOCS-065` | API, guides, examples, migration and support-disposition docs |
| `PKG-065` | package ownership, wheels/sdist, clean install, and asset inclusion |

## Entry and exit

Stage 1 entry requires a satisfied `v0.64.1` predecessor audit, accepted D-110 contracts, named
owners for #690/#693/#694/#698, the frozen scope checklist, measured budgets, and exact commands
for every gate. Exit requires no unexplained private-selector dependency, no silent CSS omission,
no unowned token or asset, no accessibility regression, and no new Supported claim for a
Progressive/Deferred surface.

## Release validation record

The locked Python 3.12 environment passes:

```text
python scripts/check_065.py --verify
ruff format --check packages tests examples
ruff check packages tests examples
pyright
pytest -q --strict-config --strict-markers
```

Observed results: all 21 phase gates pass; full tests pass (`3568 passed, 166 skipped`); Ruff
passes; and pyright reports zero errors. The release-gate command passes against this packet and
`0.65.0`; the coordinated package and runtime metadata now report `v0.65.0`.

# Hedron `v0.51` curated extras acceptance

**Status:** Planned. Stage 0 contract refined by D-088 against Published in-tree `v0.50.3`. Does **not** close `SR-021`. Does **not** ship runtime.<br>
**Planning baseline:** Published in-tree `v0.50.3`<br>
**Required predecessor/cut baseline:** Verified in-tree `v0.50.3`<br>
**Target:** Hedron `v0.51.0`<br>
**Decision/RFC:** D-087 / D-088 / [RFC-0078](../rfcs/RFC-0078-CURATED-EXTRAS-LIFECYCLE.md)<br>
**Tracking:** [#507](https://github.com/eddiethedean/hedron/issues/507)<br>
**Related:** [#504](https://github.com/eddiethedean/hedron/issues/504)–[#506](https://github.com/eddiethedean/hedron/issues/506)

D-088 named shipped 0.50.3 extras seams (`hedron_extras.plugin`,
`hedron_extras.experimental`, `feature_specs`, `hedron-extras-*` hosts,
EXTRAS-025). Stage 1 may not start during this refine.

## Release contract

- Public 0.50.3 extras imports and experimental-ui quarantine stay.
- `ExtrasFeature` is additive in `hedron-extras`; it does not replace
  `FeatureBundle` or `InteractionCatalog`.
- Experimental UI (`CodeEditor`, `TerminalView`, `Joystick`, `DeviceBridge`)
  stays behind `hedron[experimental-ui]` and does not graduate.
- `BrowserPythonSandbox` stays Experimental and is not in Supported
  `hedron[extras]`; Stage 1 makes default plugin registration opt-in.
- Companion #504–#506 are flagship authoring, not extras gates.
- PKG-051 upgrade source is **0.50**, not 0.49.

## Exact gate matrix

| Gate | Verified means |
|---|---|
| `INVENTORY-051` | Every feature has one honest Supported/Experimental/Deprecated/removed disposition. |
| `DESCRIPTOR-051` | Versioned `ExtrasFeature` is the package inventory authority. |
| `WORKBENCH-051` | Editor/workbench workflows are bounded, cancelable, and preserve server authority. |
| `DATA-051` | TreeView/Typeahead providers have identities, abort, races, and paged fallbacks. |
| `IMAGE-051` | Image intents use normalized schemas and server-confirmed output. |
| `INPUT-051` | Signature, clipboard, document, URL, and high-frequency inputs pass limit tests. |
| `LIFECYCLE-051` | Element/HTMX lifecycle, race, and cleanup matrices pass. |
| `BROWSER-051` | Three-engine, keyboard/touch, theme, and failed-enhancement matrices pass. |
| `SECURITY-051` | Per-feature threats, CSP/offline, sandbox/device boundaries pass. |
| `SUPPLY-051` | Isolation, integrity, license/SBOM; no ambient remote assets. |
| `A11Y-051` | Semantics, instructions, reflow/zoom/contrast/motion. Not `SR-021`. |
| `VISUAL-051` | State-complete gallery including failed-enhancement. |
| `ECOSYSTEM-051` | Explorer, HDJ, catalog, scenarios, conformance, adapters. |
| `DOCS-051` | Tutorials, reference, deployment, Experimental UI risk, migration. |
| `PKG-051` | Minimal/per-feature/all wheels; 0.50 upgrade/rollback. |
| `REGRESS-051` | Fleet regression; no hidden Deferred extras claims. |

## Stage 0 checklist

- [x] D-087 and RFC-0078 define extras depth, dispositions, and exclusion boundaries.
- [x] D-088 rebases the living/planning baseline to Published in-tree `v0.50.3`.
- [x] Tracking [#507](https://github.com/eddiethedean/hedron/issues/507) bound.
- [x] Stage 0 / contract refine makes no runtime/version/living-tip claim.
- [ ] Stage 1 runtime (blocked until this packet and Verified in-tree 0.50.3).

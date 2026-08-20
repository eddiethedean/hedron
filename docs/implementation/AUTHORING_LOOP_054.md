# Authoring loop and application chrome (`v0.54`)

**Status:** Stage 0 Accepted; Stage 1 Implemented for all foundation and companion
workstreams (all fifteen `*-054` gates Verified). Living tip is `v0.54.0`
(Published in-tree; tag/PyPI deferred).<br>
**Tracking:** [#538](https://github.com/eddiethedean/hedron/issues/538)–[#543](https://github.com/eddiethedean/hedron/issues/543);
companions [#523](https://github.com/eddiethedean/hedron/issues/523)–[#537](https://github.com/eddiethedean/hedron/issues/537)<br>
**Decision/RFC:** D-093, refined by D-094 /
[RFC-0081](../rfcs/RFC-0081-AUTHORING-LOOP-AND-CHROME.md)<br>
**Planning baseline:** Published in-tree `v0.53.0`<br>
**Target:** Hedron `v0.54.0` (in-tree Published; Git tag / PyPI upload deferred)

## Consume shipped, do not fork (D-094)

- Sample kit: Callout plugin, `hedron.plugins` entry, Explorer panel
- Simulator: `SimApp`, `embed_demo`, `require_supported_*`, `UnsupportedSimFeatureError`
- Notebook: `start_preview`, `NotebookPreview`, token gate, localhost defaults
- Fleet: `hedron fleet` / Explorer health with `package_doctor: False`
- Theme/chrome: `Theme`, `REQUIRED_A11Y_TOKENS`, `AppShell`, layout builtins
- Application DX (0.53): assets, diagnostics, routes, workflow, testgen, discover, fleet
- Shared schema path: `hedron_conformance.authoring_loop`

## Stage 1 seam map

| Workstream | Issue | Gates | Focus |
|---|---|---|---|
| Sample / doctor | #538 | `SAMPLE-054`, `DOCTOR-054` | Modular kit + package doctor |
| Simulator | #539 | `SIM-054`, `PARITY-054` | Subset/divergence + parity |
| Notebook lifecycle | #540 | `NOTEBOOK-054`, `LIFECYCLE-054` | Display handles + cleanup |
| Security / topology | #541 | `SECURITY-054`, `TOPOLOGY-054` | Boundaries + non-loopback |
| Ecosystem / matrices | #542 | `ECOSYSTEM-054`, `COMPAT-054`, `PLATFORM-054` | Public-contract loop |
| Exit | #543 | `A11Y-054`, `DOCS-054`, `PKG-054`, `REGRESS-054` | Docs/a11y/pkg/regress |
| Chrome companions | #523–#537 | fold into ecosystem/a11y/docs | Design system + #528 fixture |

## Architecture

```text
hedron_conformance.authoring_loop   shared fixture + diagnostic schema
       │
       ├── hedron-sample-kit variants + hedron package doctor
       ├── hedron-sim subset/divergence + recording + parity
       ├── hedron-notebook handles + handoff + topology
       └── hedron-core Theme/AppShell/layout chrome (#523–#537)
```

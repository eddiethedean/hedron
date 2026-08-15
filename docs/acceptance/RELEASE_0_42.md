# Hedron `v0.42` production-grade Web Component platform acceptance

**Status:** Verified in-tree as Published **`v0.42.0`** (tag/PyPI deferred). Stage 0 baseline was Published **`v0.41.0`**.

Phase 0.42 graduates `hedron-elements` and a locked first-party Supported element inventory to
production-grade for declared workflows only, with compatibility, independent review, element
human-AT honesty, performance, supply evidence, and the locked 32-issue medium/low fleet
remediation packet. Owning decision: [D-070](../DECISIONS.md). Design:
[RFC-0060](../rfcs/RFC-0060-WEB-COMPONENT-PLATFORM.md) (**Accepted**; Resolved questions
(D-070)). Plan: [HEDRON_ELEMENTS_042](../implementation/HEDRON_ELEMENTS_042.md). Evidence index:
[`release-gate-0.42.toml`](release-gate-0.42.toml). Capability inventory:
[`supported-element-inventory-042.toml`](supported-element-inventory-042.toml). Fleet inventory:
[`production-grade-inventory-042.toml`](production-grade-inventory-042.toml). Tracking:
[#97](https://github.com/eddiethedean/hedron/issues/97) (stale 0.38 title/body superseded by
D-066/D-070). Medium/low remediations (issue bodies remain normative; `REGRESS-042` Verified only
when closed):
[#99](https://github.com/eddiethedean/hedron/issues/99),
[#100](https://github.com/eddiethedean/hedron/issues/100),
[#108](https://github.com/eddiethedean/hedron/issues/108),
[#136](https://github.com/eddiethedean/hedron/issues/136),
[#137](https://github.com/eddiethedean/hedron/issues/137),
[#138](https://github.com/eddiethedean/hedron/issues/138),
[#139](https://github.com/eddiethedean/hedron/issues/139),
[#140](https://github.com/eddiethedean/hedron/issues/140),
[#141](https://github.com/eddiethedean/hedron/issues/141),
[#145](https://github.com/eddiethedean/hedron/issues/145),
[#146](https://github.com/eddiethedean/hedron/issues/146),
[#147](https://github.com/eddiethedean/hedron/issues/147),
[#148](https://github.com/eddiethedean/hedron/issues/148),
[#151](https://github.com/eddiethedean/hedron/issues/151),
[#152](https://github.com/eddiethedean/hedron/issues/152),
[#156](https://github.com/eddiethedean/hedron/issues/156),
[#160](https://github.com/eddiethedean/hedron/issues/160),
[#174](https://github.com/eddiethedean/hedron/issues/174),
[#175](https://github.com/eddiethedean/hedron/issues/175),
[#177](https://github.com/eddiethedean/hedron/issues/177),
[#187](https://github.com/eddiethedean/hedron/issues/187),
[#205](https://github.com/eddiethedean/hedron/issues/205),
[#206](https://github.com/eddiethedean/hedron/issues/206),
[#208](https://github.com/eddiethedean/hedron/issues/208),
[#217](https://github.com/eddiethedean/hedron/issues/217),
[#218](https://github.com/eddiethedean/hedron/issues/218),
[#238](https://github.com/eddiethedean/hedron/issues/238),
[#242](https://github.com/eddiethedean/hedron/issues/242),
[#243](https://github.com/eddiethedean/hedron/issues/243),
[#245](https://github.com/eddiethedean/hedron/issues/245),
[#246](https://github.com/eddiethedean/hedron/issues/246),
[#249](https://github.com/eddiethedean/hedron/issues/249).

`AT-042` is element-inventory honesty on the D-052 matrix. It does **not** claim Supported
product-wide human AT and does **not** close [#86](https://github.com/eddiethedean/hedron/issues/86)
/ `SR-021`. Scoped AT skeleton: [human-at/042](human-at/042/PROTOCOL.md).

## Release contract at cut

- Coordinated Hedron train: `v0.42.0`; `hedron-elements` Beta production-grade for the declared
  Supported inventory only (pin `>=0.42.0,<0.43`).
- Machine-readable Supported inventory of stable tags, ABI versions, attributes/properties, events,
  form encodings, slots/parts/tokens, fallback, browser floor, packages, and exclusions.
- Named Supported `ElementStateOwnership` modes, `InteractionState` transitions,
  `OptimisticMutation` types, `GestureOverlayCatalog` entries; React-island remains Experimental.
- Minimum/current browsers/dependencies, mixed 0.36–0.41 versions, upgrades, rollback, offline,
  package removal, CDN refusal, and incompatible/unknown feature fallback.
- Independent browser/security review with zero unresolved critical/high findings.
- Element human AT for representative form, navigation, data-editor, chart, and swap/failure
  workflows (plus default-presentation public form/settings/table/dialog); unproven surfaces stay
  outside Supported inventory.
- Reference-app bundle/request/upgrade/interaction/memory/leak/long-task/layout-shift budgets plus
  wheel/npm/module/worker/WASM/source/license/SBOM/provenance/rollback evidence.
- Medium/low remediation packet closed at `REGRESS-042`.

## Exact cut matrix

| Lane | Required proof | Command |
|---|---|---|
| Stable inventory | Machine inventory of tags/ABI/events/forms/tokens/fallback | `check_stable_042.py` |
| Compatibility | Browser/package matrices, upgrade/rollback/offline/removal | `check_compat_042.py` |
| Review | Independent threat review; zero unresolved critical/high | `check_review_042.py` |
| Human AT | Element workflows remediated/dispositioned; inventory honest | `check_at_042.py` |
| Performance | Reference-app loading, upgrade, interaction, memory/leak budgets | `check_perf_042.py` |
| Supply | Wheel/npm SBOM, provenance, license, vulnerability, rollback | `check_supply_042.py` |
| Regression | Hosts/HDJ/plugins/conformance + exact 32-issue packet | `check_regress_042.py` |
| Packaging | Inventory, docs, supply, release rehearsal | `verify_pkg_42.py` |

Commands are names reserved by this plan, not implementations.

## Stage 0 entry/exit

- [x] D-070 Accepted and RFC-0060 Accepted (Resolved questions (D-070) present)
- [x] Gate manifest, implementation plan, Supported element inventory, upgrade fixture, review brief,
  production-grade inventory, and AT-042 skeleton exist
- [x] Tracking issue [#97](https://github.com/eddiethedean/hedron/issues/97) is bound to every
  0.42 gate and the locked 32-issue remediation set
- [x] `v0.41.0` is Published; living baseline for this refine is `v0.41.0`
- [x] Stage 0 / contract refine makes no runtime/version/living-tip claim

## Verification

During planning:

```bash
python scripts/verify_pkg_42.py --allow-planned
```

At cut:

```bash
python scripts/verify_pkg_42.py
python scripts/check_release_gate.py 0.42.0 --execute-verified
```

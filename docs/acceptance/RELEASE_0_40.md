# Hedron `v0.40` Web Component authoring and interoperability acceptance

**Status:** Published as `v0.40.0` (2026-08-14). All owned
gates Verified; React-island remains Experimental docs/reference only per D-068.

Phase 0.40 enables third-party authors to build portable Hedron elements without private
APIs, publishes a React migration matrix with an Experimental island bridge (docs/reference
only), and aligns plugins, HDJ, Explorer, themes, and conformance on shared element metadata.
Evidence is indexed by [`release-gate-0.40.toml`](release-gate-0.40.toml). **Zero Deferred**
among 0.40-owned rows at cut, except React-island may remain Experimental per D-068.

Owning decision: [D-068](../DECISIONS.md). Design:
[RFC-0060](../rfcs/RFC-0060-WEB-COMPONENT-PLATFORM.md) (**Accepted**). Implementation:
[HEDRON_AUTHORING_040](../implementation/HEDRON_AUTHORING_040.md). Catalogs:
[REACT_MIGRATION_MATRIX_040.md](../implementation/REACT_MIGRATION_MATRIX_040.md) ·
[WEB_COMPONENT_INTERACTION_CONTRACTS.md](../implementation/WEB_COMPONENT_INTERACTION_CONTRACTS.md).
Capability inventory:
[`authoring-capability-inventory-040.toml`](authoring-capability-inventory-040.toml). Tracking:
[#95](https://github.com/eddiethedean/hedron/issues/95). Medium/low remediations (issue bodies
remain normative; `REGRESS-040` Verified only when closed):
[#162](https://github.com/eddiethedean/hedron/issues/162),
[#203](https://github.com/eddiethedean/hedron/issues/203),
[#204](https://github.com/eddiethedean/hedron/issues/204),
[#219](https://github.com/eddiethedean/hedron/issues/219),
[#220](https://github.com/eddiethedean/hedron/issues/220),
[#222](https://github.com/eddiethedean/hedron/issues/222).

Scoped AT for authoring/theme surfaces uses [human-at/040](human-at/040/PROTOCOL.md). It does
**not** claim Supported human AT ([#86](https://github.com/eddiethedean/hedron/issues/86) /
`SR-021`).

## Release contract at cut

- Coordinated Hedron train: `v0.40.0`.
- Public author kit and `hedron new element` scaffold with external consumer plugin proof.
- HDJ / plugin / Explorer / theme metadata parity for element ABI declarations.
- `ReactMigrationMatrix` with dispositions `native` / `hedron` / `element` / `react-island` /
  `not-a-fit`; Experimental React-island bridge as docs/reference only (not inside
  `hedron-elements`).
- Optional `@hedron/elements` modules/TS types only; Python no-Node path unchanged.
- If npm mirror ships: wheel↔npm content identity, provenance/SBOM/license evidence.
- Browser evidence: Chromium, Firefox, and WebKit on recorded exact versions.
- Medium/low remediation packet #162/#203/#204/#219/#220/#222 closed at `REGRESS-040`.

## Exact cut matrix

| Lane | Required proof | Command |
|---|---|---|
| Author kit | Public contracts + `hedron new element` scaffold | `check_author_040.py` |
| Plugin consumer | Separately built plugin using public metadata only | `check_plugin_040.py` |
| HDJ | Standards-native element markup + static declarations | `check_hdj_040.py` |
| Theme | Scoped styles, tokens, parts/slots, forced-color/print | `check_theme_040.py` |
| Explorer | Full element inspection / failure simulation | `check_explorer_040.py` |
| Conformance | Portable positive/negative fixtures | `check_conf_040.py` |
| Migrate | React matrix, worked migrations, bounded island bridge | `check_migrate_040.py` |
| Supply | Wheel/npm identity, provenance, SBOM, licenses | `check_supply_040.py` |
| Regression | Upgrades from `v0.39.0`, browsers/hosts, 6-issue packet | `check_regress_040.py` |
| Packaging | Inventory, docs, supply, release rehearsal | `verify_pkg_40.py` |

## Stage 0 entry/exit

- [x] D-068 Accepted and RFC-0060 Accepted (Resolved questions (D-068) present)
- [x] Gate manifest, implementation plan, capability inventory, upgrade fixture, review brief,
  production-grade inventory, migration catalog, and scoped AT-040 skeleton exist
- [x] Tracking issue [#95](https://github.com/eddiethedean/hedron/issues/95) is bound to every
  0.40 gate and the locked 6-issue remediation set
- [x] `v0.39.0` is Published; living baseline for this refine is `v0.39.0`
- [x] Stage 0 / contract refine makes no runtime/version/living-tip claim

## Verification

During planning:

```bash
python scripts/verify_pkg_40.py --allow-planned
```

At cut:

```bash
python scripts/verify_pkg_40.py
python scripts/check_release_gate.py 0.40.0 --execute-verified
```

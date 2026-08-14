# Upgrade fixtures — phase 0.40 authoring and interoperability

Stage 0 contract refine baseline: living Published `v0.39.0`. Runtime implementation begins at
Stage 1. Cut target: Hedron `v0.40.0`. Tracking
[#95](https://github.com/eddiethedean/hedron/issues/95).

## Required upgrade corpus

- Element authoring / plugin / HDJ / Explorer / theme metadata from `v0.39.0` remains readable;
  unknown 0.40 declarations fail closed with named diagnostics.
- `hedron new element` scaffold outputs install and build without private imports.
- ReactMigrationMatrix fixtures cover each disposition (`native` / `hedron` / `element` /
  `react-island` / `not-a-fit`) with honest non-fits.
- Experimental React-island reference unmounts cleanly and never claims HTMX region ownership.
- Optional `@hedron/elements` modules/types (if shipped) do not require an application bundler
  for Python consumers.
- The locked 6-issue remediation corpus under #95 remains cited until each issue is closed at
  `REGRESS-040` Verified.

## Pin migration at cut

| Surface | Before (living tip) | At phase 0.40 cut |
|---|---|---|
| Hedron train | `hedron>=0.39.0,<0.40` | `hedron>=0.40.0,<0.41` |
| Author kit / scaffold | Not Supported | Public contracts + `hedron new element` |
| React islands | Not Supported | Experimental docs/reference only |
| `@hedron/elements` | Absent / provisional | Modules + TS types only (optional) |

## Rollback

Rollback pins `hedron>=0.39.0,<0.40`, removes 0.40-only author/island/npm assets, and verifies no
stale custom-element definition or island root remains. Browser-local island state is disposable.

## Required artifacts

- before/after scaffold trees, metadata goldens, and Explorer inspection traces;
- matrix disposition fixtures and non-fit documentation;
- three-browser island mount/unmount and cache/version-skew tests;
- clean wheelhouse (and npm, if shipped) install for 0.39 → 0.40 and rollback documentation;
- remediation fixtures for #162/#203/#204/#219/#220/#222.

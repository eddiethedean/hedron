# What's new in 0.42

!!! note "Historical release note"

    This page records the 0.x release named in its title. For current installation,
    support, and published 1.0 status, use [Current release and support](current-release.md).
    Keep the historical pins below only when maintaining that release line.

**Published `v0.42.0`**. Owning decision: D-070.
Tracking: [#97](https://github.com/eddiethedean/hedron/issues/97).

For new apps, use the current compatibility floor `hedron>=1.0.0`; see [Current release and support](current-release.md).

## Highlights

- Graduates **`hedron-elements`** from Alpha incubator to **Beta**, production-grade
  for the locked Supported inventory only (`>=0.42.0,<0.43`).
- Machine-readable Supported tags: `hedron-example`, `hedron-field-text`,
  `hedron-field-choice`, `hedron-field-file`, `hedron-disclosure`, `hedron-dialog`,
  `hedron-action-async`, and `hedron-data-editor` (plus cross-referenced
  `hedron-chart` from `hedron-charts` `>=0.2.0,<0.3`).
- Compatibility, independent security review, element human-AT honesty (`AT-042`),
  performance budgets, and supply evidence for the Supported inventory.
- Closes the locked 32-issue medium/low fleet remediation packet (`REGRESS-042`).

## What this is not

- Not a promotion of every experimental element/backend.
- Not product-wide Supported human AT (`SR-021` / #86 remains distinct).
- Not Hedron `1.0` or a PyPI Production/Stable claim for `hedron-elements`.

## Upgrade

Historical 0.42 pin was `hedron>=0.42.0,<0.43`. For new apps, use
`hedron>=1.0.0` (and the current `hedron-elements` compatibility line when used).
Rollback of a 0.42-era app: pin `>=0.41.0,<0.42`. See [Upgrade](upgrade.md) · [What's ready](whats-ready.md) ·
[Roadmap](https://github.com/eddiethedean/hedron/blob/main/docs/ROADMAP.md).

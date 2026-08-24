# What's new in 0.62

Phase 0.62 is the verified in-tree release candidate for navigation, bounded optimism, failure
isolation, and stable identity transfer.

## Highlights

- Generation-safe navigation with canonical URL, title, history, focus, and scroll handling.
- Ordinary-link and enhancement-disabled fallbacks remain first-class.
- Same-origin safe-prefetch and capability-detected view-transition policies.
- Bounded optimistic mutation with revision, idempotency, confirmation, rollback, and conflict
  reconciliation.
- Localized failure boundaries with explicit retry, propagation, and uncertain-outcome handling.
- Stable identity targets and bounded schema-compatible state transfer.

Progressive dashboard fan-out is explicitly omitted from the 0.62 Supported claim. The latest
public PyPI release remains 0.61.0 until the 0.62 tag and upload are completed.

See the [0.62 acceptance packet](https://github.com/eddiethedean/hedron/blob/main/docs/acceptance/RELEASE_0_62.md), [interaction API coverage](../api/INTERACTION_062.md),
and [upgrade guidance](upgrade.md).

# What's new in Hedron 0.37

**Published** as `v0.37.0`. Historical pin: `hedron>=0.37.0,<0.38`.
For new apps, use `hedron>=0.52.0,<0.53`; see [What’s new in 0.51](whats-new-0.51.md).

Phase **0.37** ships Alpha **hedron-elements 0.37.0** with form-associated reference controls, an `InteractionState` bridge, semantic primitives, and high-severity remediations #230–#237 plus follow-on #244.

## hedron-elements

- **Form fields:** `hedron-field-text`, `hedron-field-choice`, `hedron-field-file`
- **Primitives:** `hedron-disclosure`, `hedron-dialog`
- **Async reference:** `hedron-action-async` with shared `InteractionState`
- **Bridge modules:** `interaction-state.mjs`, `gesture-catalog.mjs`
- **Unchanged:** `hedron-example` ABI from 0.36

## Train pin

Install with `hedron-elements>=0.37.0,<0.38` for the historical 0.37 cut, or pin
`hedron>=0.52.0,<0.53` / `hedron[elements]>=0.50.1,<0.51` for the living tip.

## Not in 0.37

Chart runtime (0.38), OptimisticMutation (0.39), React bridge (0.40), production-grade Web Components graduation (0.42).

## See also

[RFC-0060](https://github.com/eddiethedean/hedron/blob/main/docs/rfcs/RFC-0060-WEB-COMPONENT-PLATFORM.md) ·
[RELEASE_0_37](https://github.com/eddiethedean/hedron/blob/main/docs/acceptance/RELEASE_0_37.md) ·
[Upgrade](upgrade.md)

# What's new in Hedron 0.37

Phase **0.37** ships Alpha **hedron-elements 0.37.0** with form-associated reference controls, an `InteractionState` bridge, semantic primitives, and high-severity remediations #230–#237 plus follow-on #244.

## hedron-elements

- **Form fields:** `hedron-field-text`, `hedron-field-choice`, `hedron-field-file`
- **Primitives:** `hedron-disclosure`, `hedron-dialog`
- **Async reference:** `hedron-action-async` with shared `InteractionState`
- **Bridge modules:** `interaction-state.mjs`, `gesture-catalog.mjs`
- **Unchanged:** `hedron-example` ABI from 0.36

## Train pin

Install with `hedron-elements>=0.38.0,<0.39` and matching Hedron train packages.

## Not in 0.37

Chart runtime (0.38), OptimisticMutation (0.39), React bridge (0.40), production-grade Web Components graduation (0.42).

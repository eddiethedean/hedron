# `Auto`

**Status:** Accepted

`Auto(value)` selects an appropriate component through the registered intelligent-rendering pipeline.

```python
Page(Auto(users_dataframe))
```

## Baseline mappings

- Hedron component → unchanged component.
- Dataframe-like or rows → `DataTable` or policy-selected `DataEditor`.
- Plotly, Altair, or Matplotlib object → corresponding chart adapter.
- Markdown value → secure `Markdown` component.
- PIL-like image → managed `Image` component.
- Mapping → `DescriptionList` or JSON viewer under policy.
- Sequence → list or table according to shape.

Selection is deterministic. Each renderer declares supported types, priority, cost, optional package, security implications, and explanation metadata. Ambiguous matches produce a documented winner or an actionable error; they never depend on import order.

The Data Intelligence Layer may inspect schema, size, cardinality, datetime columns, and geographic fields to recommend presentation. Expensive inspection is bounded and cannot implicitly collect a lazy dataset. `as_=` and policy options provide explicit override.

Explorer shows the selected renderer, candidates, rejected candidates, inspection evidence, and payload implications.


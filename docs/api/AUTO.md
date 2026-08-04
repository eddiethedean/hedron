# `Auto`

!!! note "Stability (0.8 compatibility baseline)"

    Classifications for this surface are recorded in [STABILITY.md](STABILITY.md).
    Package maturity (Beta/Alpha) is separate from API level (`beta` / `experimental` /
    `internal` / `deferred`).

**Status:** Accepted · **Shipped** (core `hedron` — **no** `hedron[data]` extra)

`Auto(value)` selects an appropriate component through the registered intelligent-rendering
pipeline.

```python
from hedron import Auto, Hedron, Page

app = Hedron(title="Auto", security="standard", session_secret="replace-me")


@app.page("/")
def home() -> Page:
    return Page(Auto({"name": "Ada", "role": "admin"}), title="Auto")
```

## Constructor

```python
Auto(value=None, *, as_=None)
```

| Parameter | Type | Meaning |
|---|---|---|
| `value` | `Any` | Object to render |
| `as_` | `str \| type \| None` | Force a registered renderer id/type when inference is ambiguous |

## Returns

A component node suitable for composition under `Page` / fragments. Selection is
deterministic for a given registry and value shape.

## Baseline mappings

- Hedron component → unchanged component
- Mapping → `DescriptionList` (or JSON viewer under policy)
- Sequence → list or table according to shape
- Markdown-like string policy → secure `Markdown` when registered
- Dataframe-like / tabular rows → may select `DataTable` **when** `hedron[data]` is installed
- Plotly / Altair / Matplotlib → chart adapters **when** `hedron[charts]` (+ backend) is installed
- PIL-like image → managed `Image` when helpers are available

Ambiguous matches produce a documented winner or an actionable error; they never depend
on import order. Expensive inspection is bounded.

## Errors

| Situation | Behavior |
|---|---|
| No renderer for value | Diagnostic / render error with explanation metadata |
| Optional package missing for chosen renderer | Import/extra error — install `hedron[data]` or `hedron[charts]` as needed |
| Ambiguous match without `as_` | Documented winner or actionable error |

## See also

- [Component gallery — Auto](../components/auto.md)
- [Data applications](../guides/data-apps.md) · [Data](DATA.md)

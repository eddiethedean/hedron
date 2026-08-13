# `Auto`

!!! note "Stability"

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
| `as_` | `str \| None` | Force a registered renderer **name** when inference is ambiguous or you need an explicit winner |

## Returns

A component node suitable for composition under `Page` / fragments. Selection is
deterministic for a given registry and value shape.

## Baseline mappings

- Hedron component → unchanged component
- Mapping → `DescriptionList` (or JSON viewer under policy)
- Sequence → list or table according to shape
- Markdown-like string policy → secure `Markdown` when registered
- Dataframe-like / tabular rows → may select `DataTable` **when** `hedron[data]` is installed
- Plotly / Altair / Matplotlib → chart adapters when the in-repo chart provider is
  available from PyPI at the documented compatibility floor
- PIL-like image → managed `Image` when helpers are available

Ambiguous matches produce a documented winner or an actionable error; they never depend
on import order. Expensive inspection is bounded.

## Errors

| Situation | Behavior |
|---|---|
| No renderer matched the value | Raises with code **`HED-AUTO-0001`** (“No Auto renderer matched…”) |
| Unknown `as_` renderer name | Raises with code **`HED-AUTO-0001`** (unknown forced renderer) |
| Optional package missing for chosen renderer | Install `hedron[data]>=0.33.0,<0.34` for data or `hedron[charts]>=0.33.0,<0.34` for charts |
| Ambiguous match without `as_` | Documented winner when the registry can pick one; otherwise **`HED-AUTO-0001`** |

## See also

- [Component gallery — Auto](../components/auto.md)
- [Data applications](../guides/data-apps.md) · [Data](DATA.md)
- [Error codes](../guides/error-codes.md)

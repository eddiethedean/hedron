---
status: shipped
---

# `Component`

!!! note "Stability"

    Classifications for this surface are recorded in [STABILITY.md](STABILITY.md).
    Package maturity (Beta/Alpha) is separate from API level.

**Status:** Accepted · **Shipped** (introduced in 0.4; current train **0.20.0**)

`Component` is the base class for reusable server-rendered UI.

```python
from hedron import Card, Component, Props, Text
from hedron_core import NodeLike


class UserCardProps(Props):
    name: str


class UserCard(Component[UserCardProps]):
    props_type = UserCardProps

    def __init__(self, *, name: str, **kwargs: object) -> None:
        super().__init__(UserCardProps(name=name, **kwargs))

    def render(self) -> NodeLike:
        return Card(Text(self.props.name))
```

`NodeLike` is exported from **`hedron_core`**, not `hedron`. Day-to-day composition
often returns built-ins (`Card`, `Text`, …) without naming `NodeLike` explicitly.

## Constructor / subclass surface

| Member | Type | Description |
|---|---|---|
| `props_type` | `type[Props]` | Declared props model (required on concrete subclasses) |
| `__init__(props)` / typed kwargs | — | Validates props via the declared model |
| `props` | `Props` | Immutable validated props for this instance |
| `render()` | `-> NodeLike` | Pure render; **no hidden I/O** |

## Returns

| Method | Returns |
|---|---|
| `render()` | `NodeLike` — components, native nodes, strings, supported sequences, or `None` |
| Top-level `render(...)` engine | `RenderResult` with HTML / diagnostics (not produced inside `Component.render`) |

## Errors

| Condition | Typical outcome |
|---|---|
| Invalid props | Validation error at construction |
| Unsupported child values in helpers | Type-aware render/diagnostics error |
| Calling `render()` for side effects / I/O | Contract violation (must not perform hidden I/O) |

## Contract

- Construction validates the declared props contract.
- `render()` performs no hidden I/O and returns `NodeLike`; the top-level rendering engine alone produces `RenderResult`.
- Props are immutable for the duration of rendering.
- Text values are escaped; native attributes are normalized and context checked.
- Children and named slots follow the component’s declared cardinality.
- Components may declare examples, documentation, styles, and browser assets.

Composition helpers accept components, native nodes, strings, supported sequences, and `None`; unsupported arbitrary values produce a type-aware error. `Auto()` inference ships in core `hedron` — see [Auto](AUTO.md). Install `hedron[data]` for DataTable/DataEditor.

Component identity is deterministic for diagnostics and targets when requested. It excludes secret values and is never an authorization mechanism.

## Component folders

Discovered component folders may include `component.py`, `styles.css`, `browser.mjs`, and
`examples.py`. Jinja templates live in explicit application or package loader namespaces and are
not inferred from component folders.

## See also

- [Models and Props](MODELS.md) · [Page](PAGE.md) · [Built-ins](BUILT_INS.md)
- Component gallery pages under `docs/components/`

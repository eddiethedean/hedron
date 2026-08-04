---
status: shipped
---

# `Component`


!!! note "Stability (0.8 compatibility baseline)"

    Classifications for this surface are recorded in [STABILITY.md](STABILITY.md). Package maturity (Beta/Alpha) is separate from API level (`beta` / `experimental` / `internal` / `deferred`).

**Status:** Accepted · **Shipped in 0.4**

`Component` is the base protocol for reusable server-rendered UI.

```python
from hedron import Card, Component, Props, Text
from hedron_core import NodeLike


class UserCardProps(Props):
    name: str


class UserCard(Component[UserCardProps]):
    def render(self) -> NodeLike:
        return Card(Text(self.props.name))
```

`NodeLike` is exported from **`hedron_core`**, not `hedron`. Day-to-day composition
often returns built-ins (`Card`, `Text`, …) without naming `NodeLike` explicitly.

## Contract

- Construction validates the declared props contract.
- `render()` performs no hidden I/O and returns `NodeLike`; the top-level rendering engine alone produces `RenderResult`.
- Props are immutable for the duration of rendering.
- Text values are escaped; native attributes are normalized and context checked.
- Children and named slots follow the component’s declared cardinality.
- Components may declare examples, documentation, styles, and browser assets.

Composition helpers accept components, native nodes, strings, supported sequences, and `None`; unsupported arbitrary values produce a type-aware error. `Auto()` inference is available on the 0.6 train — see [Auto](AUTO.md) (`pip install "hedron[data]"` for data-oriented renderers).

Component identity is deterministic for diagnostics and targets when requested. It excludes secret values and is never an authorization mechanism.

Applications normally subclass `Component` or compose built-ins in functions. The optional
`hedron-jinja` package composes trusted application templates in phase 0.9; it does not replace this
canonical Python contract. Internal node classes are not a stability promise unless listed here.

## Component folders

Discovered component folders may include `component.py`, `styles.css`, `browser.mjs`, and
`examples.py`. Jinja templates live in explicit application or package loader namespaces and are
not inferred from component folders.

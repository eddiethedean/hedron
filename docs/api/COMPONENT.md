# `Component`

**Status:** Proposed

`Component` is the base protocol for reusable server-rendered UI.

```python
from hedron import Component, Card, Text

class UserCard(Component[UserCardProps]):
    def render(self) -> ComponentNode:
        return Card(Text(self.props.user.name))
```

## Contract

- Construction validates the declared props contract.
- `render()` performs no hidden I/O and returns a supported node or render result.
- Props are immutable for the duration of rendering.
- Text values are escaped; native attributes are normalized and context checked.
- Children and named slots follow the component’s declared cardinality.
- Components may declare examples, documentation, styles, and browser assets.

Composition helpers accept components, native nodes, strings, supported sequences, and `None`; unsupported arbitrary values produce a type-aware error and may recommend `Auto()`.

Component identity is deterministic for diagnostics and targets when requested. It excludes secret values and is never an authorization mechanism.

Applications normally subclass `Component`, compose built-ins in functions, or author HDN-backed components. Internal node classes are not a stability promise unless listed in this API set.


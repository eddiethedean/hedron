---
status: shipped
---

# `Model`, `Props`, `FormModel`, and `EventPayload`

!!! note "Stability (0.8 compatibility baseline)"

    Classifications for this surface are recorded in [STABILITY.md](STABILITY.md).

**Status:** Accepted · **Shipped**

Hedron exposes purpose-specific model bases backed by Pydantic.

```python
from hedron import Field, FormModel, Model, Props

class User(Model):
    id: int
    name: str

class UserCardProps(Props):
    user: User
    compact: bool = False

class CreateUser(FormModel):
    name: str = Field(min_length=1, label="Name")
```

## Roles

| Type | Role |
|---|---|
| `Model` | Portable domain data used by UI contracts |
| `Props` | Component construction input; never automatically exposed as HTTP input |
| `FormModel` | Client-submitted form or action input with field presentation metadata |
| `EventPayload` | Typed custom-event data crossing a browser/server boundary |

## Supported field shapes

Primitives, enums, literals, optionals, lists, string-keyed mappings, nested Hedron
models, dates, `SafeUrl`, and component-node types where declared. Extra fields are
forbidden by default. `Secret` and `TrustedHtml` follow
[security types](SECURITY_TYPES.md).

## Errors

| Situation | Behavior |
|---|---|
| Unsupported / contradictory `Field` options | Fail at class definition (`HED-MODEL-*`) |
| Arbitrary objects / callbacks as props | Fail at class definition |
| Invalid submitted payload | Pydantic/`ValidationError` in your handler |

## See also

- [Field](FIELD.md) · [Forms and actions](../guides/forms-and-actions.md)
- [Component](COMPONENT.md)

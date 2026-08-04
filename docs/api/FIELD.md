---
status: shipped
---

# `Field`

!!! note "Stability (0.8 compatibility baseline)"

    Classifications for this surface are recorded in [STABILITY.md](STABILITY.md).

**Status:** Accepted · **Shipped**

`Field` declares validation, presentation, security, and data-editing metadata.

```python
from decimal import Decimal

from hedron import Field, Model, Secret

class EmployeeRow(Model):
    employee_id: int = Field(label="ID", read_only=True)
    salary: Decimal = Field(minimum=0, display="currency")
    password: Secret = Field(autocomplete="current-password")
```

## Parameters (common)

| Parameter | Group | Meaning |
|---|---|---|
| `minimum` / `maximum` | Validation | Numeric bounds |
| `min_length` / `max_length` / `pattern` | Validation | String constraints |
| `choices` / `required` | Validation | Enumerations and required state |
| `label` / `help` / `placeholder` / `display` / `autocomplete` / `format` | Presentation | Form and table presentation |
| `read_only` / `hidden` / `secret` / `writable_policy` | Access | Access metadata (not authorization) |
| `key` / `sortable` / `filterable` / `editor` / `width` / `identity` | Data | Table/editor hints |
| `accessible_label` / `accessible_description` / `accessible_error` | Accessibility | ATIA-oriented metadata |

Unknown keyword options raise at class definition (`HED-MODEL-0002`). Contradictory
combinations (for example `read_only` with `writable_policy`) raise `HED-MODEL-0001`.

Metadata may guide forms, tables, DataEditor, examples, OpenAPI extensions, and Explorer.
It never grants authorization or replaces business validation.

## See also

- [Models](MODELS.md) · [Forms and actions](../guides/forms-and-actions.md)

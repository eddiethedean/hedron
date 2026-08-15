---
status: shipped
---

# `Field`

!!! note "Stability"

    Classifications for this surface are recorded in [STABILITY.md](STABILITY.md).

**Status:** Accepted · **Shipped** (current train **0.42.x**)

`Field` declares validation, presentation, security, and data-editing metadata on
`Model` / `FormModel` attributes. It returns a Pydantic `FieldInfo` with Hedron metadata.

```python
from decimal import Decimal

from hedron import Field, Model, Secret

class EmployeeRow(Model):
    employee_id: int = Field(label="ID", read_only=True)
    salary: Decimal = Field(minimum=0, display="currency")
    password: Secret = Field(autocomplete="current-password")
```

## Signature

```python
def Field(
    default: Any = ...,
    *,
    default_factory: Any = None,
    # Validation
    minimum: float | int | None = None,
    maximum: float | int | None = None,
    min_length: int | None = None,
    max_length: int | None = None,
    pattern: str | None = None,
    choices: list[Any] | tuple[Any, ...] | None = None,
    required: bool | None = None,
    # Presentation
    label: str | None = None,
    help: str | None = None,
    placeholder: str | None = None,
    display: str | None = None,
    autocomplete: str | None = None,
    format: str | None = None,
    # Access
    read_only: bool = False,
    hidden: bool = False,
    secret: bool = False,
    writable_policy: str | None = None,
    # Data
    key: str | None = None,
    sortable: bool = False,
    filterable: bool = False,
    editor: str | None = None,
    width: str | int | None = None,
    identity: bool = False,
    # Accessibility
    accessible_label: str | None = None,
    accessible_description: str | None = None,
    accessible_error: str | None = None,
) -> Any: ...
```

## Parameters

| Parameter | Group | Meaning |
|---|---|---|
| `default` / `default_factory` | Core | Default value or factory (Pydantic semantics) |
| `minimum` / `maximum` | Validation | Numeric bounds |
| `min_length` / `max_length` / `pattern` | Validation | String constraints |
| `choices` / `required` | Validation | Enumerations and required state |
| `label` / `help` / `placeholder` / `display` / `autocomplete` / `format` | Presentation | Form and table presentation |
| `read_only` / `hidden` / `secret` / `writable_policy` | Access | Access metadata (not authorization) |
| `key` / `sortable` / `filterable` / `editor` / `width` / `identity` | Data | Table/editor hints |
| `accessible_label` / `accessible_description` / `accessible_error` | Accessibility | ATIA-oriented metadata |

## Returns

A Pydantic `FieldInfo` carrying Hedron metadata for forms, tables, DataEditor, examples,
OpenAPI extensions, and Explorer.

## Errors

| Code | When |
|---|---|
| `HED-MODEL-0001` | Contradictory combinations (`read_only` + `writable_policy`; `secret` + `display="plaintext"`; `secret` + `identity`) |
| `HED-MODEL-0002` | Unknown keyword options in `**extra` |
| `HED-MODEL-0003`+ | Additional model/field diagnostics may appear from the model system—see [error codes](../guides/error-codes.md) and source |

Metadata may guide forms, tables, DataEditor, examples, OpenAPI extensions, and Explorer.
It never grants authorization or replaces business validation.

## See also

- [Models](MODELS.md) · [Forms and actions](../guides/forms-and-actions.md)

---
status: shipped
---

# `Field`


!!! note "Stability (0.8 freeze)"

    Classifications for this surface are recorded in [STABILITY.md](STABILITY.md). Package maturity (Beta/Alpha) is separate from API level (`beta` / `experimental` / `internal` / `deferred`).

**Status:** Accepted

`Field` declares validation, presentation, security, and data-editing metadata supported by Hedron.

```python
from decimal import Decimal

from hedron import Field, Model, Secret

class EmployeeRow(Model):
    employee_id: int = Field(label="ID", read_only=True)
    salary: Decimal = Field(minimum=0, display="currency")
    password: Secret = Field(autocomplete="current-password")
```

## Metadata groups

- Validation: minimum, maximum, length, pattern, choices, required state.
- Presentation: label, help, placeholder, display, autocomplete, format.
- Access: read-only, hidden, secret, writable policy identifier.
- Data: stable key, sortable, filterable, editor kind, width.
- Accessibility: accessible label, description, error and relationship metadata.

Metadata is declarative and statically inspectable. It may guide forms, tables, DataEditor, examples, OpenAPI extensions, and Explorer, but it never grants authorization or supplies business validation.

Unsupported or contradictory options fail when the model class is created. Secret fields are redacted from representations, examples, logs, identities, cache keys, traces, and Explorer samples.

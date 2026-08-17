---
status: planned
---

# FastAPI and Pydantic convergence

!!! warning "Planned 0.49 contract"

    This is the D-081 / RFC-0076 public contract. No 0.49 API is available until every owning
    release gate is satisfied.

## Dependency lifetimes

```python
from hedron import DependsOn, DependencyLifetime

Database = DependsOn("database", lifetime=DependencyLifetime.HANDLER)
StreamDatabase = DependsOn("database", lifetime=DependencyLifetime.RESPONSE)
```

`HANDLER` releases a yielded resource after the handler returns and before response transmission.
`RESPONSE` retains it until the response or stream completes. Background work cannot capture either
request-owned value.

## Boundary binding

Existing authoring stays valid:

```python
from typing import Annotated
from hedron import FormBody, FormModel, ViewParams

class Filters(FormModel):
    q: str = ""
    limit: int = 50

@app.refreshable("/items")
def items(filters: Annotated[Filters, ViewParams()]): ...
```

Hedron chooses `native-model` only when FastAPI's native parameter-model behavior is equivalent.
Otherwise it retains `expanded-fields`. `BoundaryBindingPlan` exposes the decision and fallback
reason; authors can force the portable fallback during migration.

## Input and output schemas

`TypeSchema` v2 records separate sanitized input and output projections. It never exposes secret
defaults, examples, executable schema hooks, request values, or serializer code. Computed fields
are output-only; sensitive inputs are write-only or absent from projections.

## Authorization declarations

```python
from hedron import RequiresScopes

@app.command("/reports/export", authorization=RequiresScopes("reports:read", "reports:export"))
def export_report(...): ...
```

Scopes are inspectable requirements, not authorization decisions. Applications still own
authentication, tenant/object policy, and denial.

## Compatibility

- Existing routes keep their current behavior unless the compiler proves native equivalence.
- HTML routes continue returning Hedron response classes.
- JSON routes may retain native FastAPI response models and serialization.
- Flask and Django compile the same declarations through their existing guard/binding seams.
- TypeSchema v1 remains readable for the documented compatibility window.
- Experimental partial validation, Pydantic `MISSING`, and `FailFast` are not Supported APIs.


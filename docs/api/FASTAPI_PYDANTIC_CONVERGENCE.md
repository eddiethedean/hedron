---
status: planned
---

# FastAPI and Pydantic convergence

!!! warning "Planned 0.49 contract"

    This is the D-081 / D-084 / RFC-0076 public contract. No 0.49 API is available
    until every owning release gate is satisfied. Planning baseline is Published
    in-tree `v0.48.0`. Tracking [#380](https://github.com/eddiethedean/hedron/issues/380).

## Dependency lifetimes

```python
from hedron import DependsOn, DependencyLifetime

Database = DependsOn("database", lifetime=DependencyLifetime.HANDLER)
StreamDatabase = DependsOn("database", lifetime=DependencyLifetime.RESPONSE)
```

Hedron names stay `handler` / `response`. FastAPI compile targets are `function` /
`request`, not `response`:

| Hedron | FastAPI |
|---|---|
| `DependencyLifetime.HANDLER` | `Depends(scope="function")` — exit after the handler returns, before the response is sent |
| `DependencyLifetime.RESPONSE` | `Depends(scope="request")` — exit after the response or stream completes |

Ordinary routes can use `HANDLER` when evidence allows. Streaming, SSE, and download
routes that still need the resource after handler return require `RESPONSE`.
Background work cannot capture either request-owned value. User-authored FastAPI
`Depends()` remains valid; `DependsOn` is additive.

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
reason; `BindingPlan` remains the structural path/query plan. Authors can force the portable
fallback during migration. Existing `ViewParams` / `FormBody` routes keep expanded-fields unless
equivalence is proven.

## Input and output schemas

`TypeSchema` v2 records separate sanitized input and output projections on top of the
existing v1 payload. It never exposes secret defaults, examples, executable schema hooks,
request values, or serializer code. Computed fields are output-only; sensitive inputs are
write-only or absent from projections. v1 artifacts remain readable during the compatibility
window.

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

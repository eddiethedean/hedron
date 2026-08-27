---
status: beta
---

# FastAPI and Pydantic convergence

Phase 0.49 (D-081 / D-084 / RFC-0076) compiles existing handle, TypeSchema, and catalog
plans onto FastAPI from the Published in-tree `v0.48.0` predecessor. Authority stays
descriptor → TypeSchema → catalog. Tracking
[#380](https://github.com/eddiethedean/hedron/issues/380). Published as in-tree
`v0.49.1`.

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
from pydantic import BaseModel
from hedron import FormBody, ViewParams

class Filters(BaseModel):
    q: str = ""
    limit: int = 50

@app.view("/items")
def items(filters: Annotated[Filters, ViewParams(source="query")]): ...
```

Hedron chooses `native-model` only when FastAPI's native parameter-model behavior is equivalent.
Otherwise it retains `expanded-fields`. `BoundaryBindingPlan` exposes the decision and fallback
reason; `BindingPlan` remains the structural path/query plan. Authors can force the portable
fallback during migration. Existing `ViewParams` / `FormBody` routes keep expanded-fields unless
equivalence is proven. Flask/Django never receive FastAPI native-model binding.

## Input and output schemas

`TypeSchema` v2 records separate sanitized input and output projections on top of the
existing v1 payload. It never exposes secret defaults, examples, executable schema hooks,
request values, or serializer code. Computed fields are output-only; sensitive inputs are
write-only or absent from projections. v1 artifacts remain readable during the compatibility
window.

## Authorization declarations

```python
from hedron import RequiresScopes

@app.action("/reports/export", authorization=RequiresScopes("reports:read", "reports:export"))
def export_report(...): ...
```

Scopes are inspectable requirements, not authorization decisions. Applications still own
authentication, tenant/object policy, and denial. Removing `RequiresScopes` returns to
existing guards.

## Compatibility

- Existing routes keep their current behavior unless the compiler proves native equivalence.
- TypeSchema v1 readers remain. CatalogEntry.kind stays `view` / `command`.
- Workbench/Posit settings keep custom loaders (`retain-custom-loader`). FailFast, Pydantic
  `MISSING`, and partial streamed validation stay research-only and are not Supported.
- `polling_only` and Deferred `MORPH-048` are unchanged.

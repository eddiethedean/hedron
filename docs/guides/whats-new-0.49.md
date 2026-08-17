# What's new in 0.49

**Published in-tree `v0.49.0`** (in-tree cut; tag/PyPI deferred). Owning decisions: D-081 / D-084.
Tracking: [#380](https://github.com/eddiethedean/hedron/issues/380).

PyPI still serves **`hedron` `0.47.0`**. First-run installs should pin `hedron>=0.47.0,<0.48`
from the registry until a later upload; in-tree pins are `hedron>=0.49.0,<0.50`.

## Highlights

- Explicit dependency lifetimes: `DependsOn` compiles `HANDLER` to FastAPI
  `Depends(scope="function")` and `RESPONSE` to `Depends(scope="request")`.
- `BoundaryBindingPlan` sits beside `BindingPlan`. Eligible query/header/cookie/non-file
  form models may use FastAPI native Pydantic parameter models; mixed path/query and files
  stay expanded-fields.
- Additive TypeSchema v2 dual projections with v1 readers still accepted.
- Tagged public-wire `kind` unions for locked families. Cached `TypeAdapter` is measured on
  non-FormBody candidates only.
- Router provenance, typed OpenAPI projection, and non-granting `RequiresScopes`.
- Workbench/Posit settings stay on custom loaders. FailFast / Pydantic `MISSING` / partial
  validation remain experimental and are not Supported.

## Fixed before first PyPI upload

None in this in-tree cut. Tag/PyPI remain deferred.

This cut does not tag Git, publish a GitHub Release, or upload PyPI.

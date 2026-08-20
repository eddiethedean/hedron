# What's new in 0.49

**Published** as `v0.49.1`. Historical pin: `hedron>=0.49.1,<0.50`.
For new apps, use `hedron>=0.52.0,<0.53`; see [What’s new in 0.51](whats-new-0.51.md).

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

- Query-only native-model `ViewParams` keep compiled `Query()` markers so GET does not 422 as a JSON body (#381).
- Page and nested-router registration after OpenAPI cache or registry seal fail closed (#382).
- Required `FormBody` commands reject non-form Content-Types with HTTP 415 `HED-TYPE-0003` (#383).
- TypeSchema sanitizer allowlists JSON Schema keywords and fail-closes unknown keys and `json_schema_extra` secrets (#384).

## 0.49.1 patch

- Django `@hedron_view` CSRF-before-handler, upload control characters, TypeSchema Field/discriminator, `default_factory`, `DependsOn(streaming=True)`, `data-hx-*` mount prefix, form-associated field double-submit, Flask `FLASK_ENV` Secure cookies, and Flask/Django production gates (#392–#401).
- Later in-tree follow-ups on the same tip close the remaining GitHub `bug` issues for this train (CSRF bytes, OutcomeMap, MCP authz, job cancel/SSE, Redis cache keyspaces, spreadsheet formulas, chart/map compile, element reconnect, and related medium/low rows).

This cut does not tag Git, publish a GitHub Release, or upload PyPI.

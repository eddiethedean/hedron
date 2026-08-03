# RFC-0016: OpenAPI

**Status:** Accepted

## Authority split

FastAPI OpenAPI remains authoritative for HTTP. Swagger and ReDoc describe inputs, status codes, security, headers, and content types. The Hedron Explorer describes components, rendering, HTMX, styles, assets, examples, and diagnostics.

Component responses are documented as `text/html` with a string schema. Component return annotations disable ordinary JSON response-model handling for that route while preserving input and security documentation.

## Extensions

`x-hedron-*` metadata may include component identifier, public/addressable status, render modes, props schema, HTMX defaults, registry group, and Explorer preview URL. Extensions must not contain secrets, absolute source paths, dependency objects, or production-only internals.

Operation IDs use deterministic categories such as `page_users`, `component_user_table`, and `action_delete_user`. Internal routes use `include_in_schema=False` by default.

## Acceptance criteria

- Generated OpenAPI validates against the supported specification version.
- JSON and component routes coexist without schema corruption.
- Security dependencies and non-200 responses remain documented.
- Schema snapshots prevent accidental metadata changes.


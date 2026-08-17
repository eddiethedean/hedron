# Phase 0.49 upgrade and rollback fixtures

**Status:** Planned<br>
**From:** Verified `v0.48.0`<br>
**To:** `v0.49.0`

Required fixtures:

1. Existing expanded-field `ViewParams` and `FormBody` routes keep signatures, validation errors,
   generated forms, CSRF, OpenAPI, catalogs, and behavior when native-model compilation is disabled.
2. Eligible query/form models move to native-model binding and produce equivalent model values,
   aliases, extra-field rejection, errors, operation ids, and adapter outcomes.
3. Mixed path/query and multipart/file models remain on expanded-fields with an inspectable reason.
4. Existing streaming/SSE/download routes retain resources through completion; ordinary routes can
   adopt handler lifetime without premature cleanup or changed output.
5. TypeSchema v1 artifacts load and upgrade deterministically to v2; rollback restores v1 readers
   without exposing output-only or secret fields.
6. Migrated tagged unions retain Python construction, schema versions, unknown-kind failure,
   redaction, and Node/Java fixtures.
7. Nested package routers preserve paths, route metadata, package provenance, OpenAPI, and seal
   behavior; no alpha router hook is required.
8. JSON routes gain typed response/OpenAPI projection without changing HTML route content,
   response classes, HTMX headers, or direct FastAPI adoption.
9. `RequiresScopes` removal returns to existing application guards with no granted access or stale
   OpenAPI requirement; Flask/Django behavior stays explicit.
10. Cached TypeAdapter rollback returns to existing parsers without losing duplicate-key, size,
    depth, canonicalization, or redaction checks.
11. Each settings candidate can adopt and revert independently with identical source precedence,
    environment behavior, digest, secrets, paths, and diagnostics.
12. Removing every experimental research flag leaves no public symbol, schema, persisted sentinel,
    provisional authoritative state, or Supported claim.


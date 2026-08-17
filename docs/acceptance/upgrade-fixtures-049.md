# Phase 0.49 upgrade and rollback fixtures

**Status:** Planned; Stage 0 contract refined by D-084<br>
**Planning baseline:** Published in-tree `v0.48.0`<br>
**From:** Verified `v0.48.0`<br>
**To:** `v0.49.0`<br>
**Decision/RFC:** D-081 / D-084 / [RFC-0076](../rfcs/RFC-0076-FASTAPI-PYDANTIC-CONVERGENCE.md)

Required fixtures:

1. Existing expanded-field `ViewParams` and `FormBody` routes keep signatures, validation errors,
   generated forms, CSRF, OpenAPI, catalogs, and behavior when native-model compilation is disabled
   or when equivalence is not proven. Today's path is
   `apply_modeled_signature` plus `PydanticBindingAdapter`.
2. Eligible query/form/header/cookie models move to native-model binding and produce equivalent
   model values, aliases, extra-field rejection, errors, operation ids, and adapter outcomes.
   `BoundaryBindingPlan` records the strategy; `BindingPlan` stays the 0.43 structural plan.
3. Mixed path/query and multipart/file models remain on expanded-fields with an inspectable reason.
4. Existing streaming/SSE/download routes retain resources through completion (`RESPONSE` /
   FastAPI `scope="request"`); ordinary routes can adopt handler lifetime
   (`HANDLER` / `scope="function"`) without premature cleanup or changed output. Consume shipped
   0.48 `SseRegion` / experimental SSE helpers; do not reopen `polling_only`.
5. TypeSchema v1 artifacts load and upgrade deterministically to v2 additive projections; rollback
   restores v1 readers without exposing output-only or secret fields. Stage 0 does not bump
   `TYPE_SCHEMA_VERSION`.
6. Migrated tagged unions retain Python construction, schema versions, unknown-kind failure,
   redaction, and Node/Java fixtures. `CatalogEntry.kind` stays `view`/`command`.
7. Nested package routers preserve paths, route metadata, package provenance, OpenAPI, and seal
   behavior; no alpha router hook is required. Late registration after `seal_registry` /
   `seal_app_catalog` / OpenAPI cache fails closed.
8. JSON routes gain typed response/OpenAPI projection without changing HTML route content,
   response classes, HTMX headers, or direct FastAPI adoption.
9. `RequiresScopes` removal returns to existing application guards with no granted access or stale
   OpenAPI requirement; Flask/Django behavior stays explicit.
10. Cached TypeAdapter rollback returns to existing parsers without losing duplicate-key, size,
    depth, canonicalization, or redaction checks. FailFast is not on this path.
11. Each settings candidate (`fastapi-workbench`, `hedron-workbench`, `hedron-posit`) can adopt
    and revert independently with identical source precedence, environment behavior, digest,
    secrets, paths, and diagnostics. `hedron.config.HedronSettings` is not a candidate.
12. Removing every experimental research flag leaves no public symbol, schema, persisted sentinel,
    provisional authoritative state, or Supported claim.

Locks: [fastapi-lifetime-049.toml](fastapi-lifetime-049.toml) ·
[fastapi-binding-049.toml](fastapi-binding-049.toml) ·
[typeschema-v2-049.toml](typeschema-v2-049.toml) ·
[fastapi-unions-openapi-049.toml](fastapi-unions-openapi-049.toml) ·
[fastapi-settings-research-049.toml](fastapi-settings-research-049.toml).

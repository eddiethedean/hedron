---
status: current
phase: "0.45"
---

# Interaction catalog and package projections

!!! note "Published 0.45 contract"

    This is the accepted D-074 / RFC-0072 public contract for phase 0.45, refined by D-077
    against Published in-tree `v0.44.0`. Implementation is the in-tree `v0.45.0` cut
    (tag/PyPI deferred). Tracking [#328](https://github.com/eddiethedean/hedron/issues/328).

Phase 0.45 gives application, tooling, adapter, and package consumers one read-only index of the
interaction contracts established by 0.43 and 0.44:

```python
catalog = app.interactions

entry = catalog.require("users.card")
print(entry.kind)                         # "view"
print(entry.descriptor_fingerprint)       # authoritative 0.43 descriptor reference
print(entry.type_schema_fingerprint)      # optional 0.44 extension reference
print(entry.projections.keys())           # bounded package namespaces
```

The catalog does not route, validate, authorize, render, or execute anything. It references the
artifacts that already own those behaviors.

## Published symbols

D-077 locks import placement the same way D-076 locked TypeSchema: portable catalog/manifest/
projection values in `hedron-core`; FastAPI compiler, `Hedron.interactions`, CLI, OpenAPI, and
scenarios in `hedron`. Re-export the portable types from `hedron` like `TypeSchema`. Names and
semantics in this contract may not drift silently during implementation.

| Symbol | Package | Role |
|---|---|---|
| `InteractionCatalog` | `hedron-core` | Immutable application-level index of catalog entries and projections. |
| `CatalogEntry` | `hedron-core` | Redacted reference to one `BaseHandleDescriptor` and optional `hedron.type` TypeSchema. |
| `InteractionManifest` | `hedron-core` | Versioned deterministic serialized catalog snapshot. |
| `PackageProjection` | `hedron-core` | Namespaced, bounded, fingerprint-bound package metadata. |
| `ProjectionDisposition` | `hedron-core` | `native_consumer`, `projection_adapter`, `compatibility_only`, or `not_applicable`. |
| `ProjectionCapability` | `hedron-core` | Capability/support/limitation record for one provider. |
| `ProjectionProvider` | `hedron-core` | Trusted registration/build protocol for producing projections. |
| `CatalogVersionError` | `hedron-core` | Manifest/catalog/projection version or fingerprint mismatch. |
| `Hedron.interactions` | `hedron` | Read-only view of the application catalog. |

The authority hierarchy and no-execution semantics are compatibility requirements and may not drift.

## Authority hierarchy

```text
0.43 base descriptor (runtime authority)
             │
             ├── optional 0.44 TypeSchema (typed extension)
             │
             ▼
      0.45 CatalogEntry (index/reference)
             │
             └── namespaced PackageProjection values (consumer metadata)
```

`CatalogEntry` and `PackageProjection` cannot override route, method, identity, app ownership,
host, target, fallback, limits, validation, effects, outcomes, response conversion, CSRF, or
authorization.

## Required 0.43/0.44 handoff

Before this API can be implemented, 0.43 and 0.44 must remain Verified in-tree with these shipped
seams (D-073 / D-076 / D-077):

- `FragmentHandle[BindT, ContentT]` and `ActionHandle[InputT, ResultT]` with exactly two slots;
- `BoundFragment[ContentT]` and `Patch[ContentT]` with one content slot;
- one versioned authoritative `BaseHandleDescriptor` (`kind` is `view` or `command`) and
  `descriptor_fingerprint` (SHA-256 canonical JSON, first 32 hex chars; does **not** hash
  `effect` or `extensions`);
- one `BindingAdapter` protocol with `StructuralBindingAdapter` default;
- explicit `Form(action=handle, ...)` action/method/CSRF/fallback wiring;
- optional `TypeSchema` under `hedron.type` (`schema_version=1`) accessed with
  `type_schema_from_descriptor()`, fingerprinted by `TypeSchema.stable_fingerprint()`;
- closed markers `ViewParams` / `FormBody` / `Sensitive` / `InstanceKey` / `Control` /
  `Refreshes` / `Updates`; and
- `OutcomeMap(case(...), ...)` as the frozen builder spelling.

Class handlers from CLASS-044 keep the same `view`/`command` kinds. Flask/Django/Jinja remain
projection adapters stacked on
[adapter-disposition-044.toml](https://github.com/eddiethedean/hedron/blob/main/docs/acceptance/adapter-disposition-044.toml).

## `CatalogEntry`

Conceptual immutable shape:

```python
@dataclass(frozen=True, slots=True)
class CatalogEntry:
    logical_id: str
    kind: Literal["view", "command"]
    descriptor_version: int
    descriptor_fingerprint: str
    type_schema_version: int | None
    type_schema_fingerprint: str | None
    effect_state: Literal["dynamic", "observed", "declared"]
    projections: Mapping[str, PackageProjection]
    limitations: tuple[str, ...]
```

Optional TypeSchema **references** (absent on unmodeled 0.43 entries; never a second authority):
`handler_fingerprint`, `model_fingerprint`, `boundary_sources` (`ViewParams`/`FormBody` provenance
without values), `field_paths`, `control_dispositions`, `sensitivity_flags`, `identity_flags`,
`declared_target_ids`, and `outcome_variant_ids`. `effect_state` copies
`BaseHandleDescriptor.effect`. `TypeSchema.effect_knowledge` is only `dynamic` or `declared`;
observed is never a declaration.

The concrete contract also contains bounded redacted capability and provenance fields. It never
contains handlers, callbacks, model/request instances, dependency values, credentials, current
form values, arbitrary markup, or executable code.

Field/fingerprint lock:
[catalog-entry-045.toml](https://github.com/eddiethedean/hedron/blob/main/docs/acceptance/catalog-entry-045.toml).

## `InteractionCatalog`

Conceptual operations:

```python
class InteractionCatalog:
    @property
    def fingerprint(self) -> str: ...

    @property
    def sealed(self) -> bool: ...

    def get(self, logical_id: str) -> CatalogEntry | None: ...
    def require(self, logical_id: str) -> CatalogEntry: ...
    def views(self) -> tuple[CatalogEntry, ...]: ...
    def commands(self) -> tuple[CatalogEntry, ...]: ...
    def projections(self, namespace: str) -> tuple[PackageProjection, ...]: ...
    def to_manifest(self, *, profile: str = "production") -> InteractionManifest: ...
```

Iteration and serialization order are deterministic. The catalog seals with the existing registry.
Mutation after seal fails. Reading the catalog never invokes user code.

## `PackageProjection`

Conceptual shape:

```python
@dataclass(frozen=True, slots=True)
class PackageProjection:
    namespace: str
    schema_version: int
    provider: str
    provider_version: str
    catalog_fingerprint: str
    entry_fingerprint: str | None
    capabilities: tuple[ProjectionCapability, ...]
    data: Mapping[str, JsonValue]
```

Projection data must be canonical JSON-compatible data. Namespaces are unique. Unknown projection
versions remain inspectable but are not interpreted as supported behavior. Duplicate/conflicting
providers fail registration rather than merging arbitrarily.

Providers execute only during trusted registration/build. Static analysis never imports or invokes
them. Provider absence cannot break the underlying interaction.

## `InteractionManifest`

The manifest includes:

- manifest format version and whole-document fingerprint;
- application/catalog fingerprint and generation provenance;
- deterministic entry and projection records;
- package dispositions, capabilities, limitations, and compatibility ranges;
- redaction/build profile; and
- bounded diagnostics required to explain omissions or unsupported consumers.

It excludes source paths in production, secrets, defaults/examples marked sensitive, request data,
dependencies, callbacks, model instances, remote credentials, and arbitrary executable payloads.

Conceptual APIs:

```python
manifest = catalog.to_manifest(profile="production")
manifest.write_json(build_dir / "interactions.json")

loaded = InteractionManifest.read_json(path)
loaded.validate_against(catalog)
```

Writes are atomic. Compatibility is based on manifest format and referenced artifact versions,
not the filename or application version alone. Format lock:
[manifest-format-045.toml](https://github.com/eddiethedean/hedron/blob/main/docs/acceptance/manifest-format-045.toml).

## Application and CLI surface

Planned commands:

```bash
# Trusted configured-app mode; may import through the documented app entry point.
hedron inspect interactions --app myapp:app

# Static/no-execution mode; does not import the target project.
hedron inspect interactions --static .

# Versioned machine output.
hedron inspect interactions --manifest build/interactions.json --json

# Trusted build emits interactions.json beside existing build artifacts.
hedron build
```

Human output is not a stable machine protocol. JSON output and the manifest are versioned. Static
mode labels runtime-only fields unknown and never claims a complete live catalog.

## Jinja and package consumption

Package APIs accept registered handles, bound handles, or logical ids resolved through an explicit
catalog binding. They do not accept arbitrary manifest dictionaries as executable configuration.

Conceptual Jinja helpers:

```jinja
{{ h.view(user_card.bind(user_id=user.id)) }}
{{ h.command_form(add_note, fields=[title_field, body_field]) }}
```

The environment receives registered safe helper objects. Templates do not evaluate annotations,
construct routes from manifest strings, load providers, or bypass form/CSRF/output policy. Helpers
bind to shipped `FragmentHandle.bind`, `ActionHandle.form()` for opted-in `FormBody`, and
`Form(action=handle, ...)`. Unknown `Control.kind` values remain rejected by
[type-form-inventory-044.toml](https://github.com/eddiethedean/hedron/blob/main/docs/acceptance/type-form-inventory-044.toml).

## Remote projection boundary

A package may use catalog/type facts to describe an explicit MCP or Gradio adapter. Catalog
presence never grants exposure:

```python
projection.register_command(
    add_note,
    exposure=McpExposure(
        mutation=True,
        authorize=can_add_note,
        confirmation="required",
    ),
)
```

The exposure policy is owned by the remote package, repeats live authorization, and applies its
own bounds/audit. It cannot be stored as a generic package projection and treated as authority.

## Errors

| Condition | Behavior |
|---|---|
| Descriptor/type fingerprint mismatch | `CatalogVersionError`; security-sensitive production use fails before serving. |
| Duplicate logical id or projection namespace | Registration fails atomically with both owners identified. |
| Unknown optional projection version | Underlying entry remains usable; consumer reports unsupported projection. |
| Projection exceeds schema/depth/count/byte bounds | Provider rejected; underlying interaction remains unchanged. |
| Static mode cannot know a fact | Value is `unknown` with provenance; target application is not imported. |
| Manifest required but missing/corrupt | Production startup/build check fails with regeneration guidance. |

## Compatibility

- Applications not reading the catalog behave exactly as in Verified 0.44.
- A package projection is additive and removable.
- Base descriptors and `TypeSchema` remain independently valid without a manifest.
- Existing direct package APIs remain supported.
- Rollback deletes/ignores 0.45 manifests and projections without rewriting application handlers.

## Out of scope (phase 0.46)

Phase **0.46** ([RFC-0073](https://github.com/eddiethedean/hedron/blob/main/docs/rfcs/RFC-0073-PACKAGE-NATIVE-WORKFLOWS.md))
owns `FeatureBundle`, `DataWorkspace`, chart/data link workflows, schema-aware element workflows,
and explicit `McpExposure` factories. 0.45 does not ship those types or compile package-native
workflows.

## See also

- [Refreshable views and commands](REFRESHABLE_VIEWS.md)
- [Type-driven authoring](TYPE_DRIVEN_AUTHORING.md)
- [RFC-0072](https://github.com/eddiethedean/hedron/blob/main/docs/rfcs/RFC-0072-TYPED-INTERACTION-ECOSYSTEM.md)
- [Phase 0.45 implementation requirements](https://github.com/eddiethedean/hedron/blob/main/docs/implementation/TYPED_INTERACTION_ECOSYSTEM_045.md)
- [Phase 0.45 acceptance](https://github.com/eddiethedean/hedron/blob/main/docs/acceptance/RELEASE_0_45.md)

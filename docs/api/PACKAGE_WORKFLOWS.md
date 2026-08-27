---
status: current
phase: "0.46"
---

# Package-native workflows

!!! note "Published 0.46 contract"

    This is the accepted D-075 / RFC-0073 public contract for phase 0.46, refined by D-079
    against Published `v0.45.0`. Implementation is Published `v0.46.0`.
    Tracking [#334](https://github.com/eddiethedean/hedron/issues/334).
    New symbols are **Beta**. Pin `hedron>=0.66.2,<0.67`.

Phase 0.46 lets packages assemble ordinary views, commands, components, scenarios, and catalog
projections into opt-in features. It does not add a second workflow runtime.

```python
orders = DataWorkspace(
    name="orders",
    model=Order,
    source=authorized_orders,
    policy=DataWorkspacePolicy(
        can_read=can_read_orders,
        can_create=can_create_order,
        can_edit=can_edit_order,
    ),
)

app.include_feature(orders)
```

The workspace compiles to normal refreshable views, commands, forms, effects, outcomes,
components, and a 0.45 `PackageProjection`. Applications can use or replace each explicit surface.
Sources are shipped `DataEditorSource` adapters. After include, handles appear in
`Hedron.interactions` as ordinary `InteractionCatalog` entries. `descriptor_fingerprint` and
`hedron.type` stay the 0.43/0.44 authorities.

## Common symbols

| Symbol | Package | Role |
|---|---|---|
| `FeatureBundle` | `hedron-core` | Immutable package feature registration description; no execution semantics. |
| `FeatureRequirement` | `hedron-core` | Declared package/host/browser capability required by a bundle. |
| `FeatureConflictError` | `hedron-core` | Atomic registration failure for id/route/projection/dependency conflicts. |
| `FeatureProvider` | `hedron-core` | Protocol that compiles package configuration into a `FeatureBundle`; not on the `hedron` facade. |
| `Hedron.include_feature` | `hedron` | Include one validated bundle before registry/catalog seal. |
| `DataWorkspace` | `hedron-data` | Opt-in list/detail/create/edit feature over an explicit authorized source and policy. |
| `DataWorkspacePolicy` | `hedron-data` | Explicit read/create/edit/delete/auth/optimism behavior; defaults deny mutation. |
| `ChartInteraction` | `hedron-charts` | Explicit chart event → command/effect binding. |
| `McpExposure` | `hedron-mcp` | Separate deny-by-default view/resource or command/tool exposure policy. |
| `RemoteWorkflow` | `hedron-gradio` | Allowlisted Gradio endpoint → Hedron feature adapter. |

Import placement is frozen by D-079. Portable bundle values live in `hedron-core`;
`Hedron.include_feature` lives in `hedron`; package-native types stay in their packages.
Do not reuse `FeatureManifest` or Jinja `ProviderManifest`. Independently versioned satellites
retain explicit compatibility ranges, but the no-parallel-runtime and explicit-authority rules
are fixed.

## `FeatureBundle`

Conceptual contract:

```python
@dataclass(frozen=True, slots=True)
class FeatureBundle:
    logical_id: str
    provider: str
    provider_version: str
    views: tuple[FragmentHandle[object, object], ...] = ()
    commands: tuple[ActionHandle[object, object], ...] = ()
    components: tuple[type[Component], ...] = ()
    scenarios: tuple[AppScenario, ...] = ()
    projections: tuple[PackageProjection, ...] = ()
    requirements: tuple[FeatureRequirement, ...] = ()
    dependencies: tuple[str, ...] = ()
```

Concrete typing preserves useful handle types at package-specific surfaces; the erased shape above
only illustrates the heterogeneous bundle container.

Inclusion:

- occurs before registry/catalog seal;
- validates the complete dependency graph and conflicts first;
- registers atomically or makes no changes;
- is deterministic for equivalent inputs;
- cannot override an existing handle, descriptor, type schema, route, component, asset, or
  projection namespace;
- records package provenance and capability limitations; and
- leaves no partial registry/assets/routes on failure or rollback.

Bundles may depend on other bundles through declared acyclic ids. Dynamic discovery from imports,
global state, model relations, database contents, or request data is forbidden.

## `DataWorkspace`

Conceptual configuration:

```python
class OrderInput(BaseModel):
    customer_id: UUID
    quantity: int = Field(gt=0, le=100)


orders = DataWorkspace(
    name="orders",
    model=Order,
    create_model=OrderInput,
    edit_model=OrderEdit,
    source=authorized_orders,
    policy=DataWorkspacePolicy(
        can_read=can_read_orders,
        can_create=can_create_order,
        can_edit=can_edit_order,
        delete="disabled",
        optimism="server_confirmed",
    ),
    columns=[...],
    form_overrides={...},
)
```

Supported initial surfaces:

- `orders.list_view` — bounded sort/filter/page query;
- `orders.detail_view` — explicit validated identity;
- `orders.create_command` and generated/overridden form;
- `orders.edit_command` and generated/overridden form;
- explicit success, validation, not-found, forbidden, and conflict outcomes; and
- explicit refresh/update relationships among its registered surfaces.

The source is already authorized and supplies documented query/mutation methods. A workspace does
not discover ORM models, call ambient managers, infer tenant filters, open transactions, or invent
delete behavior. Mutation defaults deny. Destructive deletion requires an application-supplied
command, policy, confirmation, fallback, and tests.

Unsupported model/control/query shapes require explicit views/forms/commands. Applications can
eject or replace any generated surface without leaving the workspace runtime-dependent.

## `ChartInteraction`

```python
sales_selection = ChartInteraction(
    chart=sales_chart,
    event="select",
    payload=SalesSelection,
    command=filter_sales,
    refreshes=[sales_table, sales_summary],
    max_items=100,
)
```

The event becomes an untrusted command input. The command and returned effect remain
authoritative. Chart interaction configuration cannot contain callbacks or executable expressions.
Cycles, fan-out, frequency, payload bytes, selection cardinality, refresh requests, and export size
are bounded.

Initial Supported `event` values are host-emitted first-party `hedron-chart` kinds plus equivalent
keyboard/tabular commands: `select`, `inspect`, `focus`, and `reset`. Export is an `ActionHandle`,
never a `ChartSpec` callback. `legend_filter`, `brush`, and `drill_intent` stay explicitly modeled but
Experimental until host emission and accessibility evidence. Optional chart adapters retain their
existing Experimental classifications.

## Schema-aware elements

The package chooses an enhanced element only when the 0.44 control schema has a declared Supported
mapping. Otherwise the native control remains.

Required parity includes:

- form name/value/content-type encoding;
- label, description, required, disabled, and read-only semantics;
- constraint and server-error presentation;
- focus and announcement behavior;
- CSRF and ordinary form submission;
- safe value retention; and
- useful pre-upgrade, failed-upgrade, and no-JavaScript behavior.

Async command elements consume explicit command/outcome state. They do not infer mutation safety or
execute a handle absent an ordinary fallback.

## `McpExposure`

```python
mcp.expose(
    orders.list_view,
    as_resource=True,
    policy=McpExposure(read_only=True, authorize=can_read_orders),
)

mcp.expose(
    orders.create_command,
    policy=McpExposure(
        mutation=True,
        authorize=can_create_order,
        confirmation="required",
        max_concurrency=4,
    ),
)
```

Exposure is separate from bundle inclusion and catalog registration. It repeats live principal and
authorization checks, applies MCP bounds/cancellation/audit, and maps results through an explicit
output policy. DOM refresh/update targets may be described but do not grant an MCP client browser
authority.

## `RemoteWorkflow`

```python
classifier = RemoteWorkflow.from_gradio(
    adapter,
    endpoint="classify",
    inputs=ClassificationInput,
    outcomes=ClassificationOutcomeMap,
    policy=RemoteWorkflowPolicy(
        authorize=can_classify,
        allow_files=True,
        max_file_bytes=5_000_000,
    ),
)

app.include_feature(classifier)
```

Remote metadata is untrusted and must match the explicit local models/mapping. Existing egress,
host allowlist, credentials, file lifecycle, job, progress, cancellation, and output policies remain
authoritative. The adapter does not embed Gradio UI or make remote endpoints discoverable from
user input.

## Workbench and scenarios

- Explorer previews bundle composition, requirements, outcomes, effects, package provenance, and
  limitations. Generated code/tests are reviewable files, not an opaque saved workflow.
- Jinja renders registered feature handles; templates cannot build or expose bundles.
- Extras callable/data workbenches use catalog/type metadata instead of arbitrary callable
  inspection.
- Notebook labs are loopback-only and use synthetic/examples or explicit application inputs.
- Sim executes a documented offline subset and refuses unsupported dependencies, remote calls,
  files, live transports, or browser authority.
- `AppScenario` and conformance fixtures exercise every modeled outcome, authorization denial,
  native/HTMX/no-JavaScript path, effects, and adapter limitation.

## Errors

| Condition | Behavior |
|---|---|
| Bundle id/route/projection conflict | `FeatureConflictError`; nothing is registered. |
| Cyclic/deep/missing bundle dependency | Inclusion fails before registry mutation. |
| Missing required package/host capability | Clear unsupported-capability error; optional requirements remain explicit. |
| Unsupported model/control/chart event | Explicit override required; no guessed surface. |
| Source or authorization policy absent | Data mutation/read surface is not registered. |
| Remote exposure absent | Catalog entry remains internal; no MCP/Gradio operation exists. |
| Enhanced element fails | Native control/form remains useful. |

## Compatibility

- 0.46 is opt-in; existing applications and package APIs behave as in Verified 0.45.
- Including no bundles adds no request-path work.
- Package features compile to existing public handles/components/catalog entries.
- Applications can adopt one package and one feature at a time.
- Rollback removes bundle inclusion and returns to explicit package/0.45 APIs.
- Independently versioned satellites retain explicit compatibility ranges and maturity labels.

## See also

See also: D-079 locks
[feature-bundle-046.toml](https://github.com/eddiethedean/hedron/blob/main/docs/acceptance/feature-bundle-046.toml),
[data-workspace-046.toml](https://github.com/eddiethedean/hedron/blob/main/docs/acceptance/data-workspace-046.toml),
[chart-interaction-046.toml](https://github.com/eddiethedean/hedron/blob/main/docs/acceptance/chart-interaction-046.toml).

- [Interaction catalog](INTERACTION_CATALOG.md)
- [Type-driven authoring](TYPE_DRIVEN_AUTHORING.md)
- [RFC-0073](https://github.com/eddiethedean/hedron/blob/main/docs/rfcs/RFC-0073-PACKAGE-NATIVE-WORKFLOWS.md)
- [Phase 0.46 implementation requirements](https://github.com/eddiethedean/hedron/blob/main/docs/implementation/PACKAGE_NATIVE_WORKFLOWS_046.md)
- [Phase 0.46 acceptance](https://github.com/eddiethedean/hedron/blob/main/docs/acceptance/RELEASE_0_46.md)

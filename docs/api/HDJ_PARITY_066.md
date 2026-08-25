# App-scoped HDJ binding (0.66)

Use a frozen binding when templates need registered handles or registry-backed application facts:

```python
from jinja2 import Environment, FileSystemLoader
from hedron_jinja import JinjaBinding, HedronJinja, maps_provider_manifest

binding = JinjaBinding.from_registry(
    app_id=app.hedron_app_id,
    handles={orders.logical_id: orders, save_order.logical_id: save_order},
    asset_hrefs={"application:css": "/static/application.css"},
    providers=(maps_provider_manifest(),),
)
templates = HedronJinja(
    Environment(loader=FileSystemLoader("templates")),
    binding=binding,
)
```

An app-bound environment exposes:

- `h_view(logical_id, **bind)` — renders one explicitly bound refreshable view;
- `h_command_form(logical_id, **form)` — renders a registered command form;
- `h_catalog_facts(logical_id)` — returns redacted portable catalog facts;
- `h_type_schema(logical_id)` — returns the registered TypeSchema mapping or `None`; and
- `h_feature_bundles()` — returns the app-scoped included bundle facts.

Per request, pass portable HTMX facts explicitly:

```python
result = templates.render(
    "orders.hdj",
    view,
    context=render_context,
    htmx=htmx_context_from_headers(request.headers),
)
```

Templates may read `hdj.app_id`, `hdj.binding_fingerprint`, `hdj.htmx`, `hdj.themes`,
`hdj.application_styles`, and `hdj.providers`. Style facts are redacted and never expose local
source paths. Provider facts are declarations, not installation or authorization.

`AssetMeta.path` is deliberately not treated as a browser URL. Pass an explicit `asset_hrefs`
mapping for registry assets the application has mounted publicly; unlisted registry paths remain
outside the template environment.

Legacy explicit `components=` and `assets=` construction remains supported. Logical-ID rendering is
available only when the corresponding live handle is explicitly present in `JinjaBinding.handles`.
Descriptors and manifest dictionaries are never executable.

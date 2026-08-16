# Plugin authoring

First-party and third-party plugins register components, assets, and optional Explorer
panels through the portable plugin protocol. Study
[`hedron-sample-kit`](https://github.com/eddiethedean/hedron/tree/main/packages/hedron-sample-kit)
alongside this guide.

Install `hedron-sample-kit>=0.1.10,<0.2` for the current compatible reference package.
Versions through `0.1.6` target older cores; see
[Compatibility](../COMPATIBILITY.md#charts-and-sample-kit-compatibility-floor).

### Workspace recipe (edit sample-kit in the monorepo)

```bash
git clone https://github.com/eddiethedean/hedron.git
cd hedron
uv sync
# Editable workspace members include packages/hedron-sample-kit:
uv run python -c "import hedron_sample_kit; print(hedron_sample_kit.__file__)"
```

Point your experiment app at the monorepo with `uv sync` when you want editable source.

## 1. Package layout

```text
my_hedron_plugin/
  pyproject.toml
  src/my_hedron_plugin/
    __init__.py
    plugin.py
    components/Callout/
      __init__.py          # Callout component + CalloutProps
      styles.css
      examples.py
```

## 2. Entry point

In `pyproject.toml`:

```toml
[project.entry-points."hedron.plugins"]
my_plugin = "my_hedron_plugin.plugin:register"
```

## 3. Register

```python
# plugin.py
from __future__ import annotations

from pathlib import Path

from hedron_core.plugins import PluginCapabilities, PluginContext, PluginMeta

_ROOT = Path(__file__).resolve().parent
_COMPONENT = _ROOT / "components" / "Callout"

PLUGIN_META = PluginMeta(
    name="my_plugin",
    version="0.1.0",  # keep aligned with your distribution version
    distribution="my-hedron-plugin",
    hedron_version=">=0.40,<0.41",
    capabilities=PluginCapabilities(python=True, styles=True, assets=True),
)


def register(ctx: PluginContext) -> None:
    ctx.register_component(
        logical_id="my-hedron-plugin:callout.Callout",
        name="Callout",
        module="my_hedron_plugin.components.Callout",
        distribution="my-hedron-plugin",
        props_model="CalloutProps",
        styles_path=str(_COMPONENT / "styles.css"),
        folder_path=str(_COMPONENT),
        asset_roots=(str(_COMPONENT),),
        examples=("default",),
    )


register.PLUGIN_META = PLUGIN_META  # type: ignore[attr-defined]
```

## 4. Version gates

- `PLUGIN_META.version` should match the published package version
- `hedron_version` constrains which Hedron trains load the plugin
- Incompatible plugins fail at load with `HED-PLUGIN-0002` — do not silently no-op

## 5. Custom elements (0.40)

Third-party elements register through public `PluginContext` APIs — never private registry
imports:

```python
def register(ctx: PluginContext) -> None:
    ctx.register_asset(
        logical_id="my-plugin:probe.mjs",
        kind="module",
        path="static/ext-probe.mjs",
        digest="sha256-...",
        content_type="text/javascript",
    )
    ctx.register_element_definition(
        logical_id="my-plugin:probe",
        tag_name="ext-probe",
        abi_version=1,
        module_asset_id="my-plugin:probe.mjs",
        events=("hedron:ready",),
        parts=("root",),
        slots={"default": "Primary content"},
        tokens=("--ext-probe-accent",),
        first_party=False,
    )
```

Scaffold a starter plugin with:

```bash
hedron new element my-probe
```

Validate author metadata with `hedron_elements.author.validate_element_author_meta`.
External consumer proof:
[`examples/element-author-plugin`](https://github.com/eddiethedean/hedron/tree/main/examples/element-author-plugin).

React migration dispositions (`native` / `hedron` / `element` / `react-island` /
`not-a-fit`) live in
[REACT_MIGRATION_MATRIX_040](https://github.com/eddiethedean/hedron/blob/main/docs/implementation/REACT_MIGRATION_MATRIX_040.md).
The React-island bridge is **Experimental docs/reference only** — not Supported and not
shipped inside `hedron-elements`.

## 6. Assets, CSP, and Explorer

- Prefer package resources for assets; avoid remote asset URLs unless policy allows
- Do not ship active script / dangerous URL schemes in registered SVG icons
- Optional: `ctx.register_explorer_panel(...)` for Explorer UI (see sample kit)
- Optional: `ctx.register_diagnostic_owner("HED-MINE-")` for plugin-owned codes

## 7. Test without FastAPI

```python
from hedron_core.plugins import PluginContext
from my_hedron_plugin.plugin import PLUGIN_META, register

def test_registers() -> None:
    ctx = PluginContext(PLUGIN_META)
    register(ctx)
    # assert registry contains your logical_id / assets
```

Load the plugin in CI via the same entry-point path production uses.

## 8. Publish and version

- Pin against `hedron-core` (and optionally `hedron`) with an upper bound matching the
  adopter train (for example `>=0.44.0,<0.45`).
- Declare license metadata; do not pull FastAPI/Flask/Django into a core-facing package.
- Ship a CHANGELOG and document Experimental vs Supported claims honestly
  ([What’s ready](whats-ready.md)).
- Prefer extras so absent features add **no** import or asset cost.

## 9. Security review checklist

- No raw request/session/DB handles crossed into `hedron-core` types
- Assets and HTML use SafeUrl / TrustedHtml where required
- Explorer panels and diagnostics never leak secrets
- Deny-by-default for specialty capabilities (see sample kit / extras specialty surfaces)
- Document failure modes (missing extras, fail-closed policies)

## See also

- [Using plugins](plugin-consumer.md) (adopter enablement) · [Plugins API](../api/PLUGINS.md) ·
  [Error codes](error-codes.md) · [STABILITY](../api/STABILITY.md)
- Sample kit: `packages/hedron-sample-kit`
- Element author example: `examples/element-author-plugin`
- Layout rules: [PROJECT_LAYOUT](https://github.com/eddiethedean/hedron/blob/main/docs/PROJECT_LAYOUT.md)
- [What’s new in 0.40](whats-new-0.41.md)
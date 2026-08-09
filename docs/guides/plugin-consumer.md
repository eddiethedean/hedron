# Using plugins (consumer guide)

How to **install, enable, and review** third-party Hedron plugins in an application.
To *write* a plugin, see [Plugin authoring](plugin-authoring.md) and the
[Plugins API](../api/PLUGINS.md).

## Defaults

| `[tool.hedron].plugins` | Behavior |
|---|---|
| omit / unset | Discover and load **all** `hedron.plugins` entry points |
| `[]` | Load **none** (deny-by-default) |
| `["name", …]` | Load **only** those plugin names; missing names raise `HED-PLUGIN-MISSING` |

Production apps that do not intentionally use plugins should set `plugins = []`.

```toml title="pyproject.toml"
[tool.hedron]
plugins = []   # deny-by-default until you review a plugin
```

Full key table: [Configuration](../CONFIGURATION.md).

## Install a plugin distribution

1. Add the reviewed package to your environment (same train pin as Hedron when possible).
   The sample kit is currently a **source reference only** on Hedron 0.25; its published
   releases require older `hedron-core` versions:

   ```bash
   # For a real plugin, use its reviewed distribution and compatible version pin.
   ```

2. Enable it by **name** (the entry-point key, not the PyPI distribution name):

   ```toml
   [tool.hedron]
   plugins = ["sample_kit"]
   ```

3. Restart the app. Incompatible `hedron_version` ranges fail at load (`HED-PLUGIN-0002`)
   and roll back that plugin’s contributions — they do not silently no-op.

## Review before enablement

Third-party plugins are **out of Hedron’s security scope** until you review them
([enterprise diligence](enterprise-diligence.md), [threat model](threat-model.md)).

Checklist:

- Pin the plugin distribution; prefer packages that declare `hedron_version` for your train
- Prefer local package assets over remote script/URL loads
- Inspect registered components, Explorer panels, and diagnostic prefixes
- Run `hedron check` / Explorer locally with `explorer="development"` before production
- Keep production `explorer="off"` (or `secured` with real auth)

## Troubleshooting

| Symptom | Fix |
|---|---|
| Plugin components missing | Confirm install + `plugins` allowlist name matches the entry point |
| `HED-PLUGIN-MISSING` | Name in `plugins = [...]` not discovered — install package or fix spelling |
| Load rejected / rolled back | Check `hedron_version` compatibility and contribution validation errors |
| Unexpected panels in Explorer | You are loading all entry points — set an explicit allowlist or `[]` |

## See also

[Plugin authoring](plugin-authoring.md) · [Plugins API](../api/PLUGINS.md) ·
[`hedron-sample-kit`](https://github.com/eddiethedean/hedron/tree/main/packages/hedron-sample-kit)
is a source reference on the 0.25 train; see the
[packaging limitation](../COMPATIBILITY.md#current-025-packaging-limitation-charts-and-sample-kit).

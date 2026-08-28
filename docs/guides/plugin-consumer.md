# Using plugins (consumer guide)

How to **install, enable, and review** third-party Hedron plugins in an application.
To *write* a plugin, see [Plugin authoring](plugin-authoring.md) and the
[Plugins API](../api/PLUGINS.md).

## Defaults

| `[tool.hedron].plugins` | Behavior |
|---|---|
| omit / unset (non-production) | Discover and load **all** `hedron.plugins` entry points |
| omit / unset (`HEDRON_ENV=production`) | **Deny-by-default** — load none (warn). Set an allowlist, `[]`, or accept `plugins-discover-all` |
| `[]` | Load **none** |
| `["name", …]` | Load **only** those plugin names; missing names raise `HED-PLUGIN-MISSING` |

Production apps that do not intentionally use plugins should set `plugins = []`.
Under production, omitting the key is no longer discover-all.

```toml title="pyproject.toml"
[tool.hedron]
plugins = []   # deny-by-default until you review a plugin
```

Full key table: [Configuration](../CONFIGURATION.md).

## Install a plugin distribution

1. Add the reviewed package to your environment (same train pin as Hedron when possible):

   ```bash
   # Real third-party plugin (example shape — use the vendor's pin):
   # uv add "vendor-hedron-plugin>=1.0,<2"

   uv add "hedron-sample-kit>=0.2.3,<0.3"
   ```

   Workspace details: [Plugin authoring](plugin-authoring.md#workspace-recipe-edit-sample-kit-in-the-monorepo).

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
| `HED-PLUGIN-MISSING` / `HED-PLUGIN-0001` | Name in `plugins = [...]` not discovered — install package or fix spelling (same code; constant alias) |
| Load rejected / rolled back | Check `hedron_version` compatibility and contribution validation errors |
| Unexpected panels in Explorer | You are loading all entry points — set an explicit allowlist or `[]` |

## See also

[Plugin authoring](plugin-authoring.md) · [Plugins API](../api/PLUGINS.md) ·
[`hedron-sample-kit`](https://github.com/eddiethedean/hedron/tree/main/packages/hedron-sample-kit)
is the installable reference shape on the 0.30 train.

# Plugins API

**Status:** Accepted for phase 0.4

Plugins declare an entry point in group `hedron.plugins` pointing at a callable that receives a `PluginContext`.

## Context

`PluginContext` exposes narrow registration helpers (components, browser modules, Explorer panels, diagnostic owners) and never grants private globals.

`[tool.hedron].plugins` filters enabled plugin names before import when set.

Failed compatibility or contribution validation rolls back the temporary registry builder.

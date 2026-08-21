# What's new in 0.46

**Published `v0.46.0`.** Owning decisions: D-075 / D-079.
Tracking: [#334](https://github.com/eddiethedean/hedron/issues/334).

For new apps, pin `hedron>=0.58.0,<0.59`; see [What’s new in 0.51](whats-new-0.51.md).

Package-native typed workflows assemble ordinary 0.43–0.45 handles into opt-in features.
Maintainer contracts (decisions / RFC) sit in GitHub, not this adopter page.

## Highlights

- **`FeatureBundle`** is an immutable registration unit. `Hedron.include_feature` atomically
  includes one bundle before registry/catalog seal. Bundles are not executors.
- **`DataWorkspace`** produces a bundle over an explicit `DataEditorSource` and
  `DataWorkspacePolicy`. Beginner spelling: `app.include_feature(orders)`.
- **`ChartInteraction`** maps Supported events `select` / `inspect` / `focus` / `reset` onto
  registered `ActionHandle`s. Export is an `ActionHandle`. `legend_filter` / `brush` /
  `drill_intent` stay Experimental.
- Schema-aware elements are opt-in (`ActionHandle.form(enhance="elements")`). Native
  `ActionHandle.form()` remains canonical.
- **`McpExposure`** and **`RemoteWorkflow`** wrap live MCP/Gradio registration. Catalog presence
  never grants exposure.

This is not a workflow executor, inferred authz, automatic MCP/Gradio exposure, or a Supported
human AT claim.

## Layers

1. **Bundles** — atomic include, conflicts, eject, rollback.
2. **Workspaces and charts** — explicit sources, policies, and event→command graphs.
3. **Remote and workbenches** — opt-in MCP/Gradio plus Explorer/Jinja/CLI inspection.

## Compatibility

Historical 0.46 pin was `hedron>=0.46.0,<0.47`. For new apps, pin `hedron>=0.58.0,<0.59`.
Rollback of a 0.46-era app: pin `>=0.45.0,<0.46`. Apps that never call
`include_feature` stay request-path identical to 0.45.

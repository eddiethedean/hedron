# What's new in 0.44

**Published `v0.44.0`** (in-tree cut; tag/PyPI deferred). Owning decisions: D-072 / D-073 / D-076.
Tracking: [#318](https://github.com/eddiethedean/hedron/issues/318).

## Highlights

Type-driven authoring is opt-in on top of 0.43 refreshable views and commands:

- **`ViewParams` / `FormBody`** mark one Pydantic model as the bindable or form boundary.
- **`Sensitive` / `InstanceKey` / `Control` / `Refreshes` / `Updates`** are immutable annotation metadata.
- **`ActionHandle.form()`** generates native forms for the closed field inventory.
- Declared effects are checked against returned `refresh()` / `PatchSet` values; they never execute.
- **`OutcomeMap(case(...), ...)`** maps discriminated results; arbitrary `BaseModel` returns are not auto-rendered.
- Optional **`RefreshableView` / `CommandHandler`** classes compile to the same handles as functions.
- Tooling consumes one redacted **`TypeSchema`** under `hedron.type`.

This is not a new client runtime, type-checker plugin, or Supported human AT claim.

## Fixes in this cut

- Generated `ActionHandle.form()` CSRF tokens resolve at render time (#319).
- `Field.alias` is the public form/query name and does not crash Path registration (#320).
- `FormBody` commands reject JSON with HTTP 415 instead of executing on defaults (#321).

## Layers

1. **Functions and models** — one `ViewParams` or `FormBody` model on a decorated function.
2. **Forms and effects** — generated native forms, `Refreshes`/`Updates`, `OutcomeMap`.
3. **Optional classes** — `RefreshableView` / `CommandHandler` for teams that want load/render split.
4. **Escape hatches** — unmodeled 0.43 `bind`/`Form(action=handle)`/dynamic effects remain.

## Upgrade

Pin the train to `hedron>=0.44.0,<0.45`. Rollback: pin `>=0.43.0,<0.44`. See
[Upgrade](upgrade.md) · [Type-driven authoring](../api/TYPE_DRIVEN_AUTHORING.md) ·
[Roadmap](../ROADMAP.md).

# What's new in 0.43

**Published `v0.43.0`**. Owning decisions: D-071 / D-073.
Tracking: [#311](https://github.com/eddiethedean/hedron/issues/311).

For new apps, pin `hedron>=0.50.1,<0.51`; see [What’s new in 0.50](whats-new-0.50.md).

## Highlights

Refreshable views and commands are the high-level interface for server-rendered partial updates:

- **`@app.refreshable`** returns a `FragmentHandle` that owns route, host, bind, refresh, and patches.
- **`@app.command`** returns an `ActionHandle` for POST+CSRF mutations with ordinary HTTP fallback.
- **`refresh(view)`** compiles to bounded HTMX events that rerun the view GET. It is not atomic.
- **`Patch` / `PatchSet` / `patches()`** compile into the existing `InteractionResult` / OOB stack.
- Flask and Django convert the portable update values; FastAPI owns the decorator/handle ergonomics.
- `hedron new` scaffolds a handle-first hello refresh. Low-level `region` / `swap` APIs remain.

Authoring model: views render, commands do work, commands refresh views.

## Layers

1. **Handles** — `FragmentHandle`, `BoundFragment`, `ActionHandle`, `@app.refreshable`, `@app.command`.
2. **PatchSet** — `refresh()`, `Patch`, `PatchSet`, `patches()`, `compile_to_interaction`.
3. **Protocol** — generated ids/events, descriptor fingerprint, structural `BindingAdapter`.

## What this is not

- Not a reactive client runtime, custom element, or required extra JS asset.
- Not generated model forms, declared effects, or handler classes (those wait for 0.44).
- Not a replacement for `@app.fragment` / `@app.action` / `InteractionResult`.
- Not a new Supported human-AT claim.

## Upgrade

Historical 0.43 pin was `hedron>=0.43.0,<0.44`. For new apps, pin `hedron>=0.50.1,<0.51`.
Rollback of a 0.43-era app: pin `>=0.42.0,<0.43`. Generated view/command ids
are not rollback-stable. See [Upgrade](upgrade.md) · [Refreshable views](../api/REFRESHABLE_VIEWS.md)
· [Roadmap](https://github.com/eddiethedean/hedron/blob/main/docs/ROADMAP.md).

# Authoring guide

Write ordinary Markdown and compile it into a deterministic manifest-backed Hedron application.

!!! info "Native rendering"
    Prose, links, images, code, alerts, tables, and tabs render through Hedron components.

=== "Check"
    ```bash
    hedron-docs check hedron-docs.toml
    ```
=== "Serve"
    ```bash
    hedron-docs serve hedron-docs.toml
    ```

| Command | Purpose |
| --- | --- |
| `check` | Validate without writing output |
| `build` | Write the immutable site manifest |
| `serve` | Run the local preview application |

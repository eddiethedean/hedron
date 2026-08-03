# Testing API

**Status:** Accepted for phase 0.4

Import helpers from `hedron.testing`:

- `render_html` / `assert_renders` for component trees
- `fragment_client` for HTMX-style fragment requests
- `override_dependencies` for isolated examples
- `named_example` / `iter_named_examples` for registry examples
- `normalize_snapshot_html` for documented nondeterminism only

Optional browser extras live under `hedron.testing.browser` and require `hedron[browser]`.
